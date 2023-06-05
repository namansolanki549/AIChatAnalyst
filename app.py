import streamlit as st
import preprocessor, helper
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

st.sidebar.title('AI Chat Analyst')
uploaded_file = st.sidebar.file_uploader('Choose a file')
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode('utf-8')
    df = preprocessor.preprocess(data)
    
#     st.dataframe(df)
    
    # getting group name incase group chat is uploaded
    group_name = st.sidebar.text_input('Group Name (incase group chat is uploaded)')
    
    # fetch user list
    user_list = df['sender'].unique().tolist()
    if group_name is not None and group_name != '' and group_name in user_list:
        user_list.remove(group_name)
    user_list.sort()
    user_list.insert(0, 'Overall')
    phrase_gram_count = st.sidebar.text_input('No. of words in phrase count (2 by default)')
    keyword = st.sidebar.text_input('Any keyword you want to track in chat?')
    
    selected_user = st.sidebar.selectbox('Show analysis for', user_list)
    num_messages, num_words, num_media, num_links = helper.fetch_stats(selected_user, df)
    
    if st.sidebar.button('Show Analysis'):
        st.title('Top Statistics', help='General statistics of chat')
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.subheader('Total Messages')
            st.title(num_messages)
        
        with col2:
            st.subheader('Total Words')
            st.title(num_words)
            
        with col3:
            st.subheader('Media Shared')
            st.title(num_media)
        
        with col4:
            st.subheader('Links Shared')
            st.title(num_links)
            
        if selected_user == 'Overall':
            st.title('Users Activity', help='Shows activity of users like users who text most and timeline of messages')
            x, new_df = helper.most_busy_users(df)
            fig = make_subplots(rows=1, cols=2)


            col1, col2 = st.columns(2)

            with col1:
                st.subheader('Busiest Users', help='Users who message the most')
                fig.add_trace(
                go.Bar(x=x['sender'], y=x['message']),
                row=1, col=1)
                fig.update_layout(

                yaxis_title="No. of Messages",
                font=dict(
                    family="Courier New, monospace",
                    size=18,
                    color="RebeccaPurple"
                    )
                )
                st.plotly_chart(fig)

            with col2:
                st.subheader('Percentage Messages by Each User')
                if group_name is not None:
                    new_df = new_df[new_df['name']!=group_name]
                st.dataframe(new_df)


        # Message timeline
        st.subheader('Activity Timeline', help='Time-series data for no. of messages by each user. (Crop/ Zoom for detailed view')
        message_timeline_df = helper.n_messages_timeline(selected_user, df)
        fig = px.line(message_timeline_df, x="date", y="message", color='sender', markers=True)
        fig.update_layout(
            title={
            'text': 'Message timeline (Day-wise)',
            'x': 0.5,
            'y': 0.95,
            'xanchor': 'center',
            'yanchor': 'top'
            },

            xaxis_title="Time",
            yaxis_title="No. of Messages (Day)",
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="RebeccaPurple"
            )
        )
        
        st.plotly_chart(fig)
        
        
        
        # Activity Map
        st.subheader('Activity Map', help='Shows users activities day and month wise')
        fig = make_subplots(rows=1, cols=2)
        
        col1, col2 = st.columns(2)

        with col1:
            day_activity = helper.day_activity_map(selected_user, df)
            fig.add_trace(
            go.Bar(x=day_activity['day_name'], y=day_activity['n_messages'],marker=dict(color='orange')),
            row=1, col=1)
        
        with col2:
            month_activity = helper.month_activity_map(selected_user, df)
            fig.add_trace(
            go.Bar(x=month_activity['month_name'], y=month_activity['n_messages'],marker=dict(color='yellow')),
            row=1, col=2)
        fig.update_layout(
        title={
        'text': 'User Activity Maps',
        'x': 0.5,
        'y': 0.95,
        'xanchor': 'center',
        'yanchor': 'top'
        },
        yaxis_title="No. of Messages",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="RebeccaPurple"
            ),
        showlegend=False

        )
        st.plotly_chart(fig)
        
        st.subheader('Day Activity Heatmap', help='Dark colors show low activity and brighter ones shows more activities. This might help you understand, when to have conversations in your chat')
        user_heatmap = helper.day_heatmap(selected_user, df)
        fig,ax=plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)
        
                
        # WordCloud
        st.title('Most Spoken Words and Phrases', help='This section contains analysis of words and phrases used in the chat')
        df_word = helper.create_wordcloud(selected_user, df)
        fig = go.Figure(go.Scatter(
        x=df_word.sort_values(by='frequency', ascending = False).head(20).index,
        y=df_word.sort_values(by='frequency', ascending = False).head(20)['frequency'],
        mode='markers',
        marker=dict(size=df_word.sort_values(by='frequency', ascending = False).head(20)['frequency']),
        marker_color='turquoise'
        ))

        # Update the layout of the bubble chart
        fig.update_layout(
            title={
            'text': 'Most Common Words Frequency Chart',
            'x': 0.5,
            'y': 0.95,
            'xanchor': 'center',
            'yanchor': 'top'
            },
            xaxis_title="Words",
            yaxis_title="Count",
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="RebeccaPurple"
            )
        )

        st.plotly_chart(fig)
        
        
        # Phrase count
        if phrase_gram_count is None or phrase_gram_count == '':
            phrase_gram_count = 2
        df_phrase = helper.get_phrases_frequency(selected_user, df, int(phrase_gram_count))
        fig = go.Figure(go.Scatter(
        x=df_phrase.sort_values(by='frequency', ascending = False).head(10).phrase,
        y=df_phrase.sort_values(by='frequency', ascending = False).head(10)['frequency'],
        mode='markers',
        marker=dict(size=df_phrase.sort_values(by='frequency', ascending = False).head(10)['frequency']),
        marker_color='red'
        ))

        # Update the layout of the bubble chart
        fig.update_layout(
            title={
            'text': 'Phrase Frequency Bubble Chart',
            'x': 0.5,
            'y': 0.95,
            'xanchor': 'center',
            'yanchor': 'top'
            },

            xaxis_title="Phrases",
            yaxis_title="Count",
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="RebeccaPurple"
            )
        )
        
        st.plotly_chart(fig)    
        
        if keyword is not None and keyword != '':
            st.subheader('Keyword Timeline Analysis')
            df_keyword = helper.keyword_timeline(selected_user, df, keyword)
            fig = px.line(df_keyword.groupby(['date', 'sender']).sum().reset_index(), x="date", y="keyword_count", color='sender', markers=True)
            fig.update_layout(
            title={
            'text': 'Keyword Timeline Analysis: {}'.format(keyword),
            'x': 0.5,
            'y': 0.95,
            'xanchor': 'center',
            'yanchor': 'top'
            },
            xaxis_title="Time",
            yaxis_title="No. of times {} was used (in a day)".format(keyword),
            font=dict(
                family="Courier New, monospace",
                size=14,
                color="turquoise"
            )    
            )
            st.plotly_chart(fig)
            
        
        # sentiment analysis
        st.header('Sentiment analysis of chat', help='Sentiment analysis of all messages using Vader sentiment analyser')
        
        st.subheader('Overall Sentiment')
        df_sentiment_timeline, df_sentiment = helper.sentiment_analysis(selected_user, df)
        colors = {'Positive': 'LightGreen', 'Negative': 'Red', 'Neutral': 'yellow'}
        fig = px.pie(df_sentiment, values='frequency', names='sentiment',color='sentiment',color_discrete_map=colors,
                     hover_data=['frequency'], hole=0.3)

        # Set title and color scale
        fig.update_traces(textinfo='percent+label')
        fig.update_layout(
        title={
        'text': 'Chat Sentiment',
        'x': 0.5,
        'y': 0.95,
        'xanchor': 'center',
        'yanchor': 'top'
        },
        font=dict(
            family="Courier New, monospace",
            size=14,
            color="turquoise"
        )    
        )
        st.plotly_chart(fig)
        
        st.subheader('Time-Series Sentiment Analysis')
        fig = px.line(df_sentiment_timeline, x="datetime", y="positive", color='sender', markers=True)
        fig.update_layout(
            title={
            'text': 'Positive Sentiment Timeline',
            'x': 0.5,
            'y': 0.95,
            'xanchor': 'center',
            'yanchor': 'top'
            },
            xaxis_title="Time",
            yaxis_title="Positive Sentiment %",
            font=dict(
                family="Courier New, monospace",
                size=14,
                color="turquoise"
            )    
            )
        st.plotly_chart(fig)
        
        fig = px.line(df_sentiment_timeline, x="datetime", y="neutral", color='sender', markers=True)
        fig.update_layout(
            title={
            'text': 'Neutral Sentiment Timeline',
            'x': 0.5,
            'y': 0.95,
            'xanchor': 'center',
            'yanchor': 'top'
            },
            xaxis_title="Time",
            yaxis_title="Neutral Sentiment %",
            font=dict(
                family="Courier New, monospace",
                size=14,
                color="turquoise"
            )    
            )
        st.plotly_chart(fig)
           
        fig = px.line(df_sentiment_timeline, x="datetime", y="negative", color='sender', markers=True)
        fig.update_layout(
            title={
            'text': 'Negative Sentiment Timeline',
            'x': 0.5,
            'y': 0.95,
            'xanchor': 'center',
            'yanchor': 'top'
            },
            xaxis_title="Time",
            yaxis_title="Negative Sentiment %",
            font=dict(
                family="Courier New, monospace",
                size=14,
                color="turquoise"
            )    
            )
        st.plotly_chart(fig)
        
        
        # Emoji Analysis
        st.title('Analysis of Emojis')
        
        df_emoji, df_sender_emoji_count = helper.emoji_analysis(selected_user, df)
        st.subheader('Emoji Percentage')

        fig = px.pie(df_emoji, values='frequency', names='emoji',
         hover_data=['frequency'], hole=0.3)

        # Set title and color scale
        fig.update_traces(textinfo='percent+label', marker=dict(colors=px.colors.qualitative.Pastel))
        fig.update_layout(
        title={
        'text': '% of emoji usage',
        'x': 0.5,
        'y': 0.95,
        'xanchor': 'center',
        'yanchor': 'top'
        },
        font=dict(
            family="Courier New, monospace",
            size=14,
            color="turquoise"
        )    
        )
        st.plotly_chart(fig)
        
        st.subheader('Sender Wise Emoji Count')
        fig = px.line(df_sender_emoji_count, x="datetime", y="n_emoji", color='sender', markers=True)
        fig.update_layout(
        title={
        'text': 'Timeline comparison of sender\'s emoji count',
        'x': 0.5,
        'y': 0.95,
        'xanchor': 'center',
        'yanchor': 'top'
        },
        xaxis_title="Time",
        yaxis_title="Count",
        font=dict(
            family="Courier New, monospace",
            size=14,
            color="turquoise"
        )    
        )
        st.plotly_chart(fig)
        
        
            
            
            
            