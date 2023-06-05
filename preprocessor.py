import pandas as pd
import re
def preprocess(data):
    pattern = r'\[(\d{2}\/\d{2}\/\d{2}), (\d{1,2}:\d{2}:\d{2} [AP]M)\] (.+?): (.+)'
    # find all the matches of the pattern in the chat data
    matches = re.findall(pattern, data)
    chat_df = []
    for match in matches:
        chat_dict = {}
        chat_dict['date'] = match[0]
        chat_dict['time'] = match[1]
        chat_dict['sender'] = match[2]
        chat_dict['message'] = match[3]
        chat_df.append(chat_dict)
    chat_df = pd.DataFrame(chat_df)
    chat_df['datetime'] = pd.to_datetime(chat_df['date'] + ' ' + chat_df['time'], format='%d/%m/%y %I:%M:%S %p')
    chat_df.drop(['date', 'time'],axis=1,inplace=True)
    chat_df['year'] = chat_df['datetime'].dt.year
    chat_df['month'] = chat_df['datetime'].dt.month_name()
    chat_df['day'] = chat_df['datetime'].dt.day
    chat_df['hour'] = chat_df['datetime'].dt.hour
    chat_df['minute'] = chat_df['datetime'].dt.minute
    chat_df['second'] = chat_df['datetime'].dt.second
    
    return chat_df