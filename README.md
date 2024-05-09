# BookSQL : A Large Scale Text-to-SQL Dataset for Accounting Domain
BookSQL: A Large Scale Text-to-SQL Dataset for Accounting Domain (Paper: [Will Update Soon]('#))

The repository contains the full codebase of experiments and results of the NAACL 2024 paper "BookSQL: A Large Scale Text-to-SQL Dataset for Accounting Domain". 

You can get BookSQL dataset from this link [Will update soon]('#').

Our contributions can be summarized as below:
* We create a new and large-scale Text-to-SQL financial dataset referred to as BookSQL. The dataset consists of a financial-accounts database of 1 million records. The corresponding natural language queries are designed to address various practical intricacies of the accounting domain. BookSQL has 100k Query-SQL pairs which is about 1.25 times the existing largest Text-2-SQL dataset: WikiSQL. In particular, for designing the queries, we consulted financial experts to understand various practical use cases. %We also plan to create a leaderboard where researchers can benchmark various Text-to-SQL models for the accounting domain. 
* We run existing state-of-the-art models (including GPT-4) for the Text-to-SQL task on BookSQL  to see the performance and analyze the shortcomings of the models trained on existing large-scale datasets such as Spider, pointing towards developing specialized models for this domain.
## License
 --

## Citation

```
@inproceedings{kumar-etal-2024-booksql,
    title = "{BookSQL}: A Large Scale Text-to-SQL Dataset for Accounting Domain",
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