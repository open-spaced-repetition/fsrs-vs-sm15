# FSRS vs SM-15
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-15-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

It is a simple comparsion between FSRS and SM-15. [compare.ipynb](./compare.ipynb) is the notebook for the comparsion. It has three features:

1. Filter out Topic and Concept in your `Repetition History.txt` and mask the Item title for privacy.
2. Convert `Repetition History.txt` to a format that can be used in FSRS.
3. Train the FSRS model with your data and compare the result with SM-15.

Due to the difference between the workflow of SuperMemo and Anki, it is not easy to compare the two algorithms. I tried to make the comparison as fair as possible. Here is some notes:
- The first interval in SuperMemo is the duration between creating the card and the first review. In Anki, the first interval is the duration between the first review and the second review. So I removed the first record of each card in SM-15 data.
- There are six grades in SuperMemo, but only four grades in Anki. So I merged 0, 1 and 2 in SuperMemo to 1 in Anki, and mapped 3, 4, and 5 in SuperMemo to 2, 3, and 4 in Anki.
- I use the expFI recorded in data as the prediction of SM-15. The probabilty of recall from SM-15 is calculated by `1 - expFI/100`. Reference: [Repetition history](https://help.supermemo.org/wiki/Repetition_history#Data_columns)
- To ensure FSRS has the same information as SM-15, I implement an [online learning](https://en.wikipedia.org/wiki/Online_machine_learning) version of FSRS. In FSRS online, each repetition is only used once. The repetitions are sorted by the review date ascending. Then FSRS will make prediction one by one and update the model after each prediction. So FSRS online has zero knowledge of the future reviews as SM-15 does.
- The results are based on the data from a small group of people. It may be different from the result of other SuperMemo users.

## Result

Total users: 17

Total repetitions: 257,313

| Algorithm | Log Loss | RMSE | Universal Metric |
| --- | --- | --- | --- |
| FSRS |0.3819 | 0.3321 | 0.0443 |
| SM-15 | 0.4323 | 0.3489 | 0.0771 |

Smaller is better.

## Why not SM-18?

Due to the limitation of SuperMemo 18, I can't export the predictions of SM-18. So I can't compare SM-18 with FSRS. If you know how to export the predictions of SM-18, please let me know.

## Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/WinstonWantsAUserName"><img src="https://avatars.githubusercontent.com/u/99696589?v=4?s=100" width="100px;" alt="Winston"/><br /><sub><b>Winston</b></sub></a><br /><a href="#data-WinstonWantsAUserName" title="Data">🔣</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/jakandy"><img src="https://avatars.githubusercontent.com/u/51024207?v=4?s=100" width="100px;" alt="andyjak"/><br /><sub><b>andyjak</b></sub></a><br /><a href="#data-jakandy" title="Data">🔣</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/leee-z"><img src="https://avatars.githubusercontent.com/u/48952110?v=4?s=100" width="100px;" alt="leee_"/><br /><sub><b>leee_</b></sub></a><br /><a href="#data-leee-z" title="Data">🔣</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/changxvv"><img src="https://avatars.githubusercontent.com/u/40617368?v=4?s=100" width="100px;" alt="changxvv"/><br /><sub><b>changxvv</b></sub></a><br /><a href="#data-changxvv" title="Data">🔣</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/reallyyy"><img src="https://avatars.githubusercontent.com/u/39750041?v=4?s=100" width="100px;" alt="reallyyy"/><br /><sub><b>reallyyy</b></sub></a><br /><a href="#data-reallyyy" title="Data">🔣</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.pleasurable-learning.com"><img src="https://avatars.githubusercontent.com/u/8341295?v=4?s=100" width="100px;" alt="Guillem Palau-Salvà"/><br /><sub><b>Guillem Palau-Salvà</b></sub></a><br /><a href="#data-guillem-palau-salva" title="Data">🔣</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/KKKphelps"><img src="https://avatars.githubusercontent.com/u/58903647?v=4?s=100" width="100px;" alt="Pariance"/><br /><sub><b>Pariance</b></sub></a><br /><a href="#data-KKKphelps" title="Data">🔣</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Satomi0626"><img src="https://avatars.githubusercontent.com/u/90490589?v=4?s=100" width="100px;" alt="Ada"/><br /><sub><b>Ada</b></sub></a><br /><a href="#data-Satomi0626" title="Data">🔣</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://www.zhihu.com/people/L.M.Sherlock"><img src="https://avatars.githubusercontent.com/u/32575846?v=4?s=100" width="100px;" alt="Jarrett Ye"/><br /><sub><b>Jarrett Ye</b></sub></a><br /><a href="https://github.com/open-spaced-repetition/fsrs-vs-sm15/commits?author=L-M-Sherlock" title="Code">💻</a> <a href="#data-L-M-Sherlock" title="Data">🔣</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/VSpade7"><img src="https://avatars.githubusercontent.com/u/46594083?v=4?s=100" width="100px;" alt="Spade7"/><br /><sub><b>Spade7</b></sub></a><br /><a href="#data-vspade7" title="Data">🔣</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/2Lavine"><img src="https://avatars.githubusercontent.com/u/43613598?v=4?s=100" width="100px;" alt="bigidea"/><br /><sub><b>bigidea</b></sub></a><br /><a href="#data-2Lavine" title="Data">🔣</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://blog.xinshijiededa.men"><img src="https://avatars.githubusercontent.com/u/20166026?v=4?s=100" width="100px;" alt="ᡥᠠᡳᡤᡳᠶᠠ ᡥᠠᠯᠠ·ᠨᡝᡴᠣ 猫"/><br /><sub><b>ᡥᠠᡳᡤᡳᠶᠠ ᡥᠠᠯᠠ·ᠨᡝᡴᠣ 猫</b></sub></a><br /><a href="#data-OverflowCat" title="Data">🔣</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/wah123wah123"><img src="https://avatars.githubusercontent.com/u/62554369?v=4?s=100" width="100px;" alt="ZebesYoshi"/><br /><sub><b>ZebesYoshi</b></sub></a><br /><a href="#data-wah123wah123" title="Data">🔣</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/jiangege"><img src="https://avatars.githubusercontent.com/u/4214901?v=4?s=100" width="100px;" alt="jiangege"/><br /><sub><b>jiangege</b></sub></a><br /><a href="#data-jiangege" title="Data">🔣</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/WolfSlytherin"><img src="https://avatars.githubusercontent.com/u/20725348?v=4?s=100" width="100px;" alt="WolfSlytherin"/><br /><sub><b>WolfSlytherin</b></sub></a><br /><a href="#data-WolfSlytherin" title="Data">🔣</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->
