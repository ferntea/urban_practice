import os
import csv
import pandas as pd

class PriceMachine():

    def __init__(self):
        self.data = []
        # Приведение синонимов к стандартным именам
        self.column_mapping = {
            'название': 'product_name',
            'продукт': 'product_name',
            'товар': 'product_name',
            'наименование': 'product_name',
            'цена': 'price',
            'розница': 'price',
            'опт': 'price',
            'мелкий опт': 'price',
            'фасовка': 'weight',
            'масса': 'weight',
            'вес': 'weight'
        }

    def correct_headers(self, folder_path=''):
        for filename in os.listdir(folder_path):
            if filename.endswith('.csv'):
                file_path = os.path.join(folder_path, filename)
                # Ввод CSV-файла в корректной кодмровке
                df = pd.read_csv(file_path, encoding='utf-16', delimiter=',')  # Change delimiter if needed

                # debugging
                print(f"Original headers in {filename}: {df.columns.tolist()}")

                # Заголовки
                df.columns = ['Index', 'Product Name', 'Weight', 'Price']  # Adjust as per your needs

                # Сохранение справленных заголовков
                df.to_csv(file_path, index=False, encoding='utf-8', sep=',')  # Change delimiter if needed
                print(f"Corrected headers in {filename}: {df.columns.tolist()}")

    def load_prices(self, folder_path=''):
        for filename in os.listdir(folder_path):
            if 'price' in filename and filename.endswith('.csv'):
                file_path = os.path.join(folder_path, filename)
                try:
                    with open(file_path, newline='', encoding='utf-8') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')  # Change delimiter if needed
                        headers = next(reader)
                        # print(f"Processing file: {filename}, Headers: {headers}")  # Debugging line
                        product_index, price_index, weight_index = self._search_product_price_weight(headers)

                        if product_index is None or price_index is None or weight_index is None:
                            print(f"Не удалось найти необходимые колонки в файле: {filename}. Пропуск.")
                            continue  # Skip this file

                        for row in reader:
                            if len(row) > max(product_index, price_index, weight_index):
                                product_name = row[product_index]
                                # print(f"Found product: {product_name}")  # Debugging line

                                price = float(row[price_index]) if row[price_index] else 0
                                weight = float(row[weight_index]) if row[weight_index] else 1
                                price_per_kg = price / weight

                                self.data.append({
                                    'name': product_name,
                                    'price': price,
                                    'weight': weight,
                                    'file': filename,
                                    'price_per_kg': price_per_kg
                                })

                except UnicodeDecodeError as e:
                    print(f"Encoding error for file {filename}: {e}")
                except Exception as e:
                    print(f"An error occurred while processing file {filename}: {e}")

        return len(self.data)

    def _search_product_price_weight(self, headers):
        product_index = None
        price_index = None
        weight_index = None
        # Find the indices based on the mapping
        for i, header in enumerate(headers):
            standard_name = self.column_mapping.get(header)
            if standard_name == 'product_name':
                product_index = i
            elif standard_name == 'price':
                price_index = i
            elif standard_name == 'weight':
                weight_index = i
        return product_index, price_index, weight_index

    def export_to_html(self, fname='output.html'):
        result = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Позиции продуктов</title>
        </head>
        <body>
            <table border="1">
                <tr>
                    <th>Номер</th>
                    <th>Название</th>
                    <th>Цена</th>
                    <th>Фасовка</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>
        '''

        for idx, item in enumerate(self.data, start=1):
            result += f'''
                <tr>
                    <td>{idx}</td>
                    <td>{item['name']}</td>
                    <td>{item['price']}</td>
                    <td>{item['weight']}</td>
                    <td>{item['file']}</td>
                    <td>{item['price_per_kg']:.2f}</td>
                </tr>
            '''
        result += '''
            </table>
        </body>
        </html>
        '''
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(result)

    def find_text(self, text):
        text = text.strip().lower()  # Trim spaces and convert to lowercase
        return [item for item in self.data if text in item['name'].lower()]

def main():
    pm = PriceMachine()
    folder_path = 'price_lists'  # Specify your folder path here
    loaded_count = pm.load_prices(folder_path)
    print(f"Загружено {loaded_count} позиций.")
    while True:
        search_text = input("Введите текст для поиска (<Ввод> для вывода всего списка, или 'exit' для выхода): ")
        if search_text.lower() == 'exit':
            print("Работа завершена.")
            break
        found_items = pm.find_text(search_text)
        found_items.sort(key=lambda x: x['price_per_kg'])
        if found_items:
            print(f"{'№':<3} {'Наименование':<40} {'Цена':<6} {'Вес':<6} {'Файл':<20} {'Цена за кг.':<10}")
            for idx, item in enumerate(found_items, start=1):
                print(
                    f"{idx:<3} {item['name']:<40} {item['price']:<6} {item['weight']:<6} {item['file']:<20} {item['price_per_kg']:<10.2f}")
        else:
            print("Товары не найдены.")
        # Ask if the user wants to export to HTML
        export_choice = input("Хотите экспортировать массив данных в HTML? (да/нет) (или <Ввод> для продолжения: ").strip().lower()
        if export_choice in ['да', 'yes']:
            pm.export_to_html('output.html')
            print("Результаты экспортированы в output.html.")


if __name__ == "__main__":
    main()