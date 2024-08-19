import pandas as pd
from datetime import datetime

def main():
    try:
        # Load the CSV file
        file_path = '/Users/datpro/Documents/gitdatpro/ff-transform-data/forex_factory_calendar_news_scraper-main/news/2024-August_news.csv'
        df = pd.read_csv(file_path)
        print("CSV file loaded successfully.")

        # Chuyển đổi cột 'date' thành datetime, thêm năm hiện tại vào nếu không có năm
        current_year = datetime.now().year
        df['date'] = pd.to_datetime(df['date'] + f' {current_year}', format='%b %d %Y')
        print("Date column converted to datetime.")

        # Lọc các dòng chỉ giữ từ tuần tới trở đi
        today = datetime.now()
        filtered_df = df[(df['date'] >= today) & (df['currency'].isin(['USD', 'GBP', 'EUR'])) & (df['impact'] == 'red')]
        print("Filtered dataframe for upcoming events.")

        # Tạo dataframe mới cho Google Calendar CSV format
        calendar_hcm_df = pd.DataFrame({
            'Subject': filtered_df['event'],
            'Start Date': filtered_df['date'].dt.strftime('%m/%d/%Y'),
            'Start Time': pd.to_datetime(filtered_df['time'], format='%I:%M%p').dt.strftime('%H:%M'),
            'End Date': filtered_df['date'].dt.strftime('%m/%d/%Y'),  # Giả sử sự kiện kết thúc cùng ngày
            'End Time': (pd.to_datetime(filtered_df['time'], format='%I:%M%p') + pd.Timedelta(hours=1)).dt.strftime('%H:%M'),
            'Description': 'High Impact Event',
            'Location': filtered_df['currency']
        })
        print("New dataframe for Google Calendar created.")

        # Trích xuất năm và tháng từ ngày đầu tiên sau khi lọc
        year_month = filtered_df['date'].dt.strftime('%Y-%m').iloc[0]

        # Định nghĩa đường dẫn tệp đầu ra với định dạng mới
        output_path = f'/Users/datpro/Documents/gitdatpro/ff-transform-data/data/silver/monthly/{year_month}-news.csv'
        calendar_hcm_df.to_csv(output_path, index=False)
        print(f"CSV file saved to {output_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
