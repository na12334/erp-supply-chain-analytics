import pandas as pd


def extract_data(file_path):
    df = pd.read_csv(file_path, encoding="latin1")

    print("Data loaded successfully")
    print("Rows:", df.shape[0])
    print("Columns:", df.shape[1])

    return df


if __name__ == "__main__":
    df = extract_data("data/raw/DataCoSupplyChainDataset.csv")

    print("\nFirst 5 rows:")
    print(df.head())
