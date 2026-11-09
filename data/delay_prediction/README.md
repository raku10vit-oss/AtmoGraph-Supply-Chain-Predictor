# SynDelay — Delivery Delay Prediction Dataset

This folder is reserved for the SynDelay dataset, which is NOT committed to Git
because the file exceeds 54 MB.

## About SynDelay

Source: Xu, Liming; Long, Yunbo; Brintrup, Alexandra.
        SynDelay: A Synthetic Dataset for Delivery Delay Prediction, 2025.
        MIM 2025 Data Challenge (https://conferences.ifac-control.org/mim2025/data-challenge/)

Licence: No explicit licence. Academic/research use only. Please cite the paper.

Stats: 155,489 order records, 41 feature columns, multiclass delivery delay label.

Key columns: payment_type, order_date, shipping_date, shipping_mode,
             order_country, order_city, order_region, market,
             latitude, longitude, product_name, product_price,
             order_item_quantity, sales, order_status, label (delay class)

## How to obtain

1. Download syndelay_v1.csv from the MIM 2025 Data Challenge repository or the paper authors.
2. Place the file at:  data/delay_prediction/syndelay_v1.csv

The file is listed in .gitignore to prevent accidental commits.

## Citation

  @article{xu2025simmd,
    title  = {SynDelay: A Synthetic Dataset for Delivery Delay Prediction},
    author = {Xu, Liming and Long, Yunbo and Brintrup, Alexandra},
    year   = {2025}
  }
