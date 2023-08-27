from fsrs_optimizer import lineToTensor, collate_fn, power_forgetting_curve, FSRS, RevlogDataset, WeightClipper
from tqdm.auto import tqdm
from sklearn.metrics import mean_squared_error, log_loss
from torch.utils.data import DataLoader
import torch
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pathlib
import json
import csv

tqdm.pandas()


def txt_to_csv(txt_file_path: pathlib.Path):

    # Function to extract keys and values from a line
    def extract_keys_values(line):
        parts = line.strip().split(" ")
        keys, values = [], []
        for part in parts:
            key, value = part.split("=")
            keys.append(key)
            values.append(value)
        return keys, values

    # Extract all unique keys from the data to form the headers
    unique_keys = set()
    with open(txt_file_path, 'r', encoding='utf-8') as txt_file:
        for line in txt_file:
            if line.startswith("ElNo"):
                keys, _ = extract_keys_values(line)
                unique_keys.update(keys)

    # Sort the keys to maintain a consistent order
    headers = sorted(list(unique_keys))

    csv_file_path = txt_file_path.with_suffix('.csv')

    # Write the data to CSV with the identified headers and considering missing values
    with open(txt_file_path, 'r', encoding='utf-8') as txt_file, open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(headers)  # Write the headers

        for line in txt_file:
            if line.startswith("ElNo"):
                keys, values = extract_keys_values(line)

                # Consider missing values by aligning with headers
                row = [None] * len(headers)
                for key, value in zip(keys, values):
                    index = headers.index(key)
                    row[index] = value

                writer.writerow(row)


def data_preprocessing(csv_file_path):
    revlogs = pd.read_csv(csv_file_path)
    # Convert the "Date" column to standard date format
    revlogs['Date'] = pd.to_datetime(
        revlogs['Date'], dayfirst=True).dt.strftime('%Y-%m-%d')

    # Sort the DataFrame by "ElNo" and "Date" (ascending for both)
    revlogs = revlogs.sort_values(by=['ElNo', 'Date'], ascending=[True, True])

    print(f"Number of repetitions: {revlogs.shape[0]}")
    print(f"Number of items: {revlogs['ElNo'].unique().shape[0]}")

    # Remove unnecessary columns
    revlogs.drop(["Difficulty", "Hour", "Postpones", "Priority"],
                 axis=1, inplace=True, errors="ignore")

    # Remove items that first row was not the first repetition
    revlogs = revlogs.groupby('ElNo').filter(lambda group: (
        group['Rep'].iloc[0] == 1) and (group['Laps'].iloc[0] == 0))
    print(f"Number of repetitions: {revlogs.shape[0]}")

    # Remove the first repetition of each item
    revlogs.drop(revlogs[(revlogs['Rep'] == 1) & (
        revlogs['Laps'] == 0)].index, inplace=True)
    print(f"Number of repetitions: {revlogs.shape[0]}")

    # Remove items that have been reset
    revlogs = revlogs.groupby('ElNo').filter(
        lambda group: (group['Grade'] > 5).sum() == 0)
    print(f"Number of repetitions: {revlogs.shape[0]}")

    # Remove items that have invalid "expFI" values
    revlogs = revlogs.groupby('ElNo').filter(
        lambda group: (group['expFI'] == 100).sum() == 0)
    print(f"Number of repetitions: {revlogs.shape[0]}")

    # Keep the first repetitions of the same item on the same day
    revlogs.drop_duplicates(
        subset=['Date', 'ElNo'], keep='first', inplace=True)
    print(f"Number of repetitions: {revlogs.shape[0]}")

    # Rank the repetitions of each item
    revlogs['i'] = revlogs.groupby('ElNo').cumcount() + 1

    # Calculate the time difference between repetitions
    revlogs['Date'] = pd.to_datetime(revlogs['Date'])
    revlogs['delta_t'] = revlogs['Date'].diff().dt.days
    revlogs['delta_t'] = revlogs['delta_t'].fillna(0)
    revlogs.loc[revlogs['i'] == 1, 'delta_t'] = 0
    revlogs['delta_t'] = revlogs['delta_t'].astype(int)

    # Rename columns to match FSRS dataset format
    revlogs.rename(columns={'ElNo': 'card_id',
                   'Date': 'review_date'}, inplace=True)

    # Convert "Grade" to "review_rating"
    # 0, 1, 2 -> 1, 3 -> 2, 4 -> 3, 5 -> 4
    revlogs['review_rating'] = revlogs['Grade'].map(
        {0: 1, 1: 1, 2: 1, 3: 2, 4: 3, 5: 4})
    revlogs['review_time'] = 0

    # Create "t_history" and "r_history" features for training FSRS
    from itertools import accumulate

    def cum_concat(x):
        return list(accumulate(x))

    t_history = revlogs.groupby('card_id', group_keys=False)['delta_t'].apply(
        lambda x: cum_concat([[int(i)] for i in x]))
    revlogs['t_history'] = [','.join(map(str, item[:-1]))
                            for sublist in t_history for item in sublist]
    r_history = revlogs.groupby('card_id', group_keys=False)[
        'review_rating'].apply(lambda x: cum_concat([[i] for i in x]))
    revlogs['r_history'] = [','.join(map(str, item[:-1]))
                            for sublist in r_history for item in sublist]

    # Create "y" label for training FSRS
    revlogs['y'] = revlogs['review_rating'].map(
        lambda x: {1: 0, 2: 1, 3: 1, 4: 1}[x])
    revlogs.dropna(inplace=True)
    print(f"Number of repetitions: {revlogs.shape[0]}")

    def remove_non_continuous_rows(group):
        discontinuity = group['i'].diff().fillna(1).ne(1)
        if not discontinuity.any():
            return group
        else:
            first_non_continuous_index = discontinuity.idxmax()
            return group.loc[:first_non_continuous_index-1]

    revlogs = revlogs.groupby('card_id', as_index=False, group_keys=False).apply(
        remove_non_continuous_rows)
    print(f"Number of repetitions: {revlogs.shape[0]}")

    return revlogs


def train(revlogs):
    revlogs = revlogs[(revlogs['i'] > 1) & (revlogs['delta_t'] > 0) & (
        revlogs['t_history'].str.count(',0') == 0)].copy()
    revlogs['tensor'] = revlogs.progress_apply(lambda x: lineToTensor(
        list(zip([x['t_history']], [x['r_history']]))[0]), axis=1)
    revlogs.sort_values(by=['review_date'], inplace=True)
    revlogs.reset_index(drop=True, inplace=True)

    model = FSRS([0.4, 0.6, 2.4, 5.8, 4.93, 0.94, 0.86, 0.01,
                 1.49, 0.14, 0.94, 2.18, 0.05, 0.34, 1.26, 0.29, 2.61])
    optimizer = torch.optim.Adam(model.parameters(), lr=8e-3)
    loss_fn = torch.nn.BCELoss(reduction='none')
    enable_experience_replay = True
    replay_steps = 32

    dataset = RevlogDataset(revlogs)
    dataloader = DataLoader(dataset, shuffle=False, collate_fn=collate_fn)
    clipper = WeightClipper()
    d = []
    s = []
    r = []

    for i, sample in enumerate(tqdm(dataloader)):
        model.train()
        optimizer.zero_grad()
        sequence, delta_t, label, seq_len = sample
        output, _ = model(sequence)
        stability, difficulty = output[seq_len-1, 0].transpose(0, 1)
        d.append(difficulty.detach().numpy()[0])
        s.append(stability.detach().numpy()[0])
        retention = power_forgetting_curve(delta_t, stability)
        r.append(retention.detach().numpy()[0])
        loss = loss_fn(retention, label).sum()
        loss.backward()
        optimizer.step()
        model.apply(clipper)

        if enable_experience_replay and (i + 1) % replay_steps == 0:
            # experience replay
            replay_dataset = RevlogDataset(revlogs[:i+1])  # avoid data leakage
            replay_generator = torch.Generator().manual_seed(42+i)
            replay_dataloader = DataLoader(replay_dataset, batch_size=(
                i + 1)//32, shuffle=True, collate_fn=collate_fn, generator=replay_generator)
            for j, batch in enumerate(replay_dataloader):
                model.train()
                optimizer.zero_grad()
                sequences, delta_ts, labels, seq_lens = batch
                real_batch_size = seq_lens.shape[0]
                outputs, _ = model(sequences)
                stabilities = outputs[seq_lens-1,
                                      torch.arange(real_batch_size), 0]
                retentions = power_forgetting_curve(delta_ts, stabilities)
                loss = loss_fn(retentions, labels).sum()
                loss.backward()
                optimizer.step()
                model.apply(clipper)

    revlogs['difficulty'] = d
    revlogs['stability'] = s
    revlogs['p'] = r

    return revlogs


def compare(revlogs):
    fsrs_metrics = {}
    sm15_metrics = {}
    revlogs['sm15_p'] = 1 - revlogs['expFI'] / 100
    FSRS_RMSE = mean_squared_error(revlogs['y'], revlogs['p'], squared=False)
    SM15_RMSE = mean_squared_error(revlogs['y'], revlogs['sm15_p'], squared=False)

    fsrs_metrics['RMSE'] = FSRS_RMSE
    sm15_metrics['RMSE'] = SM15_RMSE

    FSRS_log_loss = log_loss(revlogs['y'], revlogs['p'])
    SM15_log_loss = log_loss(revlogs['y'], revlogs['sm15_p'])

    fsrs_metrics['log_loss'] = FSRS_log_loss
    sm15_metrics['log_loss'] = SM15_log_loss

    cross_comparison = revlogs[['sm15_p', 'p', 'y']].copy()

    def get_bin(x, bins=20):
        return (np.log(np.exp(np.log(bins) * x).round()) / np.log(bins)).round(3)

    cross_comparison['SM15_B-W'] = cross_comparison['sm15_p'] - cross_comparison['y']
    cross_comparison['SM15_bin'] = cross_comparison['sm15_p'].map(get_bin)
    cross_comparison['FSRS_B-W'] = cross_comparison['p'] - cross_comparison['y']
    cross_comparison['FSRS_bin'] = cross_comparison['p'].map(get_bin)

    fig = plt.figure(figsize=(6, 6))
    ax = fig.gca()
    ax.axhline(y = 0.0, color = 'black', linestyle = '-')

    cross_comparison_group = cross_comparison.groupby(by='SM15_bin').agg({'y': ['mean'], 'FSRS_B-W': ['mean'], 'p': ['mean', 'count']})
    universal_metric = mean_squared_error(cross_comparison_group['y', 'mean'], cross_comparison_group['p', 'mean'], sample_weight=cross_comparison_group['p', 'count'], squared=False)
    fsrs_metrics['universal_metric'] = universal_metric
    cross_comparison_group['p', 'percent'] = cross_comparison_group['p', 'count'] / cross_comparison_group['p', 'count'].sum()
    ax.scatter(cross_comparison_group.index, cross_comparison_group['FSRS_B-W', 'mean'], s=cross_comparison_group['p', 'percent'] * 1024, alpha=0.5)
    ax.plot(cross_comparison_group['FSRS_B-W', 'mean'], label=f'FSRS by SM15, UM={universal_metric:.4f}')

    cross_comparison_group = cross_comparison.groupby(by='FSRS_bin').agg({'y': ['mean'], 'SM15_B-W': ['mean'], 'sm15_p': ['mean', 'count']})
    universal_metric = mean_squared_error(cross_comparison_group['y', 'mean'], cross_comparison_group['sm15_p', 'mean'], sample_weight=cross_comparison_group['sm15_p', 'count'], squared=False)
    sm15_metrics['universal_metric'] = universal_metric
    cross_comparison_group['sm15_p', 'percent'] = cross_comparison_group['sm15_p', 'count'] / cross_comparison_group['sm15_p', 'count'].sum()
    ax.scatter(cross_comparison_group.index, cross_comparison_group['SM15_B-W', 'mean'], s=cross_comparison_group['sm15_p', 'percent'] * 1024, alpha=0.5)
    ax.plot(cross_comparison_group['SM15_B-W', 'mean'], label=f'SM15 by FSRS, UM={universal_metric:.4f}')

    ax.legend(loc='lower center')
    ax.grid(linestyle='--')
    ax.set_title("SM15 vs FSRS")
    ax.set_xlabel('Predicted R')
    ax.set_ylabel('B-W Metric')
    ax.set_xlim(0, 1)
    ax.set_xticks(np.arange(0, 1.1, 0.1))

    fig.show()

    return {
        'FSRS': fsrs_metrics,
        'SM15': sm15_metrics
    }


if __name__ == "__main__":
    for file in pathlib.Path('dataset').iterdir():
        if file.is_file() and file.suffix == '.txt':
            try:
                _, user, year, month, day = file.stem.split('-')
            except:
                continue
            txt_to_csv(file)
            revlogs = data_preprocessing(file.with_suffix('.csv'))
            revlogs = train(revlogs)
            result = compare(revlogs)
            result['user'] = user
            result['date'] = f'{year}-{month}-{day}'
            result['size'] = revlogs.shape[0]
            # save as json
            pathlib.Path('result').mkdir(parents=True, exist_ok=True)
            with open(f'result/{file.stem}.json', 'w') as f:
                json.dump(result, f, indent=4)
