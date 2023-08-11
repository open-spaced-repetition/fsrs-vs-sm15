# FSRS vs. SM-18
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-1-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

It is a simple comparsion between FSRS and SM-18. There are two notebooks to run the comparsion. `convert.ipynb` converts the SM-18 data to the same format as FSRS. `compare.ipynb` compares the two spaced repetition algorithms.

Due to the difference between the workflow of SuperMemo and Anki, it is not easy to compare the two algorithms. I tried to make the comparison as fair as possible. Here is some notes:
- The first interval in SuperMemo is the duration between creating the card and the first review. In Anki, the first interval is the duration between the first review and the second review. So I removed the first record of each card in SM-18 data.
- There are six grades in SuperMemo, but only four grades in Anki. So I merged 0, 1 and 2 in SuperMemo to 1 in Anki, and mapped 3, 4, and 5 in SuperMemo to 2, 3, and 4 in Anki.
- I use the expFI recorded in data as the prediction of SM-18. The probabilty of recall from SM-18 is calculated by `1 - expFI/100`.
- The results are based on the data from a small group of people. It may be different from the result of other SM-18 users.

## Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/WinstonWantsAUserName"><img src="https://avatars.githubusercontent.com/u/99696589?v=4?s=100" width="100px;" alt="Winston"/><br /><sub><b>Winston</b></sub></a><br /><a href="#data-WinstonWantsAUserName" title="Data">🔣</a></td>
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
