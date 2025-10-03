from langchain_core.tools import tool
from pydantic import ValidationError
import pandas as pd
import os
from services.agent.tools.models import *


@tool
def get_corp_options() -> Options:
    """
    Получить список дополнительных опций и расценок для услуги 'Создание корпоративного сайта'.

    Данные загружаются из CSV-файла: data/corp.csv.
    Ожидаемые колонки в файле: 'Услуга', 'Срок (ч)', 'Стоимость (₽)'.
    Срок возвращается в часах (без конвертации в дни).
    """
    file_path = "app/services/agent/tools/data/corp.csv"

    if not os.path.exists(file_path):
        return Options(
            options=[Option(name="Ошибка: файл не найден", term=0, price=0.0)]
        )

    try:
        df = pd.read_csv(file_path)

        required_cols = {"Услуга", "Срок (ч)", "Стоимость (₽)"}
        if not required_cols.issubset(df.columns):
            missing = required_cols - set(df.columns)
            return Options(
                options=[
                    Option(
                        name=f"Ошибка: отсутствуют колонки {missing}", term=0, price=0.0
                    )
                ]
            )

        options_list = []

        for _, row in df.iterrows():
            try:
                name = str(row["Услуга"]).strip()
                if not name or name.lower() in ("nan", "none", ""):
                    continue

                hours_raw = row["Срок (ч)"]
                if pd.isna(hours_raw):
                    term = 0
                else:
                    term = int(round(float(hours_raw)))

                price_str = str(row["Стоимость (₽)"]).strip()
                price_clean = (
                    price_str.replace("\u00a0", "")
                    .replace(" ", "")
                    .replace("₽", "")
                    .replace(",", ".")
                )
                if price_clean == "":
                    price = 0.0
                else:
                    price = float(price_clean)

                option = Option(name=name, term=term, price=price)
                options_list.append(option)

            except (ValueError, TypeError, ValidationError) as e:
                options_list.append(
                    Option(
                        name=f"Некорректная опция: {row.get('Услуга', 'N/A')}",
                        term=0,
                        price=0.0,
                    )
                )

        if not options_list:
            options_list = [Option(name="Нет доступных опций", term=0, price=0.0)]

        return Options(options=options_list)

    except Exception as e:
        return Options(
            options=[
                Option(name=f"Ошибка при загрузке данных: {str(e)}", term=0, price=0.0)
            ]
        )


@tool
def get_ecom_options() -> Options:
    """
    Получить список дополнительных опций и расценок для услуги 'Создание интернет-магазина'.

    Данные загружаются из CSV-файла: data/ecom.csv.
    Ожидаемые колонки в файле: 'Услуга', 'Срок (ч)', 'Стоимость (₽)'.
    Срок возвращается в часах (без конвертации в дни).
    """
    file_path = "app/services/agent/tools/data/ecom.csv"

    if not os.path.exists(file_path):
        return Options(
            options=[Option(name="Ошибка: файл не найден", term=0, price=0.0)]
        )

    try:
        df = pd.read_csv(file_path)

        required_cols = {"Услуга", "Срок (ч)", "Стоимость (₽)"}
        if not required_cols.issubset(df.columns):
            missing = required_cols - set(df.columns)
            return Options(
                options=[
                    Option(
                        name=f"Ошибка: отсутствуют колонки {missing}", term=0, price=0.0
                    )
                ]
            )

        options_list = []

        for _, row in df.iterrows():
            try:
                name = str(row["Услуга"]).strip()
                if not name or name.lower() in ("nan", "none", ""):
                    continue

                hours_raw = row["Срок (ч)"]
                if pd.isna(hours_raw):
                    term = 0
                else:
                    term = int(round(float(hours_raw)))

                price_str = str(row["Стоимость (₽)"]).strip()
                price_clean = (
                    price_str.replace("\u00a0", "")
                    .replace(" ", "")
                    .replace("₽", "")
                    .replace(",", ".")
                )
                if price_clean == "":
                    price = 0.0
                else:
                    price = float(price_clean)

                option = Option(name=name, term=term, price=price)
                options_list.append(option)

            except (ValueError, TypeError, ValidationError) as e:
                options_list.append(
                    Option(
                        name=f"Некорректная опция: {row.get('Услуга', 'N/A')}",
                        term=0,
                        price=0.0,
                    )
                )

        if not options_list:
            options_list = [Option(name="Нет доступных опций", term=0, price=0.0)]

        return Options(options=options_list)

    except Exception as e:
        return Options(
            options=[
                Option(name=f"Ошибка при загрузке данных: {str(e)}", term=0, price=0.0)
            ]
        )


@tool
def get_landing_options() -> Options:
    """
    Получить список дополнительных опций и расценок для услуги 'Создание простого лендинга'.

    Данные загружаются из CSV-файла: data/landing.csv.
    Ожидаемые колонки в файле: 'Услуга', 'Срок (ч)', 'Стоимость (₽)'.
    Срок возвращается в часах (без конвертации в дни).
    """
    file_path = "app/services/agent/tools/data/landing.csv"

    if not os.path.exists(file_path):
        return Options(
            options=[Option(name="Ошибка: файл не найден", term=0, price=0.0)]
        )

    try:
        df = pd.read_csv(file_path)

        required_cols = {"Услуга", "Срок (ч)", "Стоимость (₽)"}
        if not required_cols.issubset(df.columns):
            missing = required_cols - set(df.columns)
            return Options(
                options=[
                    Option(
                        name=f"Ошибка: отсутствуют колонки {missing}", term=0, price=0.0
                    )
                ]
            )

        options_list = []

        for _, row in df.iterrows():
            try:
                name = str(row["Услуга"]).strip()
                if not name or name.lower() in ("nan", "none", ""):
                    continue

                hours_raw = row["Срок (ч)"]
                if pd.isna(hours_raw):
                    term = 0
                else:
                    term = int(round(float(hours_raw)))

                price_str = str(row["Стоимость (₽)"]).strip()
                price_clean = (
                    price_str.replace("\u00a0", "")
                    .replace(" ", "")
                    .replace("₽", "")
                    .replace(",", ".")
                )
                if price_clean == "":
                    price = 0.0
                else:
                    price = float(price_clean)

                option = Option(name=name, term=term, price=price)
                options_list.append(option)

            except (ValueError, TypeError, ValidationError) as e:
                options_list.append(
                    Option(
                        name=f"Некорректная опция: {row.get('Услуга', 'N/A')}",
                        term=0,
                        price=0.0,
                    )
                )

        if not options_list:
            options_list = [Option(name="Нет доступных опций", term=0, price=0.0)]

        return Options(options=options_list)

    except Exception as e:
        return Options(
            options=[
                Option(name=f"Ошибка при загрузке данных: {str(e)}", term=0, price=0.0)
            ]
        )


