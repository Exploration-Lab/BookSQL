# BookSQL : A Large Scale Text-to-SQL Dataset for Accounting Domain
BookSQL: A Large Scale Text-to-SQL Dataset for Accounting Domain (Paper: [Will Update Soon]('#))

The repository contains the full codebase of experiments and results of the NAACL 2024 paper "BookSQL: A Large Scale Text-to-SQL Dataset for Accounting Domain". 

You can get BookSQL dataset from this link [https://github.com/Exploration-Lab/BookSQL/tree/main/DATA](https://github.com/Exploration-Lab/BookSQL/tree/main/DATA).


**NOTE:** We are not releasing the Gold SQL queries for the test set as we are maintaining a [Leaderboard](https://huggingface.co/spaces/Exploration-Lab/BookSQL-Leaderboard) where a user can upload the predictions of their model and evaluate. 


Given the importance and wide prevalence of business databases across the world, the proposed dataset, BookSQL focuses on the finance and accounting domain. 
Accounting databases are used across a wide spectrum of industries like construction, healthcare, retail, educational services, insurance, restaurant, real estate, etc. Business in these industries arranges their financial transactions into their own different set of categories (called a chart of accounts [Industry Details](https://www.investopedia.com/terms/c/chart-accounts.asp) in accounting terminology. 

Text-to-SQL system developed on BookSQL will be robust at handling various types of accounting databases. The total size of the dataset is 1 million. The dataset is prepared under financial experts' supervision, and the dataset's statistics are provided in below table. The dataset consists of 27 businesses, and each business has around 35k - 40k transactions.

Our contributions can be summarized as below:
* We create a new and large-scale Text-to-SQL financial dataset referred to as BookSQL. The dataset consists of a financial-accounts database of 1 million records. The corresponding natural language queries are designed to address various practical intricacies of the accounting domain. BookSQL has 100k Query-SQL pairs which is about 1.25 times the existing largest Text-2-SQL dataset: WikiSQL. In particular, for designing the queries, we consulted financial experts to understand various practical use cases. We also plan to create a leaderboard where researchers can benchmark various Text-to-SQL models for the accounting domain. 

    **Dataset** | **\#Size** | **#DB** | **#D** | **#T/DB** | **Domain** | **ORDER BY** | **GROUP BY** | **NESTED**
    |------|-----|-----|-----|-----|-----|-----|-----|-----|
    Spider | 10,181 | 200 | 138 | 5.1 | Cross | 1335 | 1491 | 844
    WikiSQL | 80,654 | 26,521 | - | 1 | Cross | 0 | 0 | 0 
    Advising | 3,898 | 208 | 1 | 10 | Single  | 15 | 9 | 22
    BIRD | 12,751 | 95 | 37 | 7.3 | Cross | 2576 | 881 | 0 
    IMDB | 131 | 1 | 1 | 16 | Single  | 10 | 6 | 1
    Yelp | 128 | 1 | 1 | 7 | Single  | 18 | 21 | 0
    **BookSQL** | **100k** | **1** | **1** | **7** | **Single** | **17,529** | **11,508** | **4,456**


* We run existing state-of-the-art models (including GPT-4) for the Text-to-SQL task on BookSQL  to see the performance and analyze the shortcomings of the models trained on existing large-scale datasets such as Spider, pointing towards developing specialized models for this domain.

## License

<a href="https://creativecommons.org/licenses/by-nc-sa/4.0/"><img src="https://mirrors.creativecommons.org/presskit/buttons/88x31/png/by-nc-sa.png" width="120" height="50"></a>

The BookSQL dataset follows [CC-BY-NC-SA](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en) license. Users can share and adapt our dataset if they give credit to us and do not use our dataset for any commercial purposes.

## Citation

```
@inproceedings{kumar-etal-2024-booksql,
    title = "BookSQL: A Large Scale Text-to-SQL Dataset for Accounting Domain",
    author = "Kumar, Rahul and Raja, Amar and Harsola, Shrutendra and Subrahmaniam, Vignesh and Modi, Ashutosh",
    booktitle = "Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics",
    month = "march",
    year = "2024",
    address = "Mexico City, Mexico",
    publisher = "Association for Computational Linguistics",
    abstract = "Several large-scale datasets (e.g., WikiSQL, Spider) for developing natural language interfaces to databases have recently been proposed. These datasets cover a wide breadth of domains but fall short on some essential domains, such as finance and accounting. Given that accounting databases are used worldwide, particularly by non-technical people, there is an imminent need to develop models that could help extract information from accounting databases via natural language queries. In this resource paper, we aim to fill this gap by proposing a new large-scale Text-to-SQL dataset for the accounting and financial domain: BookSQL. The dataset consists of 100k  natural language queries-SQL pairs, and accounting databases of 1 million records. We experiment with and analyze existing state-of-the-art models (including GPT-4) for the Text-to-SQL task on BookSQL. We find significant performance gaps, thus pointing towards developing more focused models for this domain.",
}
```

## Contact

In case of any queries, please contact <ashutoshm.iitk@gmail.com>, <rahulkiitp@gmail.com>
