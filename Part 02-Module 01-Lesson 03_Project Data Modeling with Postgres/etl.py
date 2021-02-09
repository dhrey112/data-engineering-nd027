import os
import glob
import psycopg2
import pandas as pd
from sql_queries import *


def process_song_file(cur, filepath):
    """Do ETL on the song_data dataset to create the songs and artists table"""

    # open song file
    df = pd.read_json(filepath, lines=True)

    # insert song record
    song_data = list(df[['song_id', 'title', 'artist_id', 'year', 'duration']].values[0])
    cur.execute(insert_songs_table, song_data)

    # insert artist record
    artist_data = df[['artist_id', 'artist_name', 'artist_location', 'artist_latitude', 'artist_longitude']].values[0]
    cur.execute(insert_artists_table, artist_data)


def process_log_file(cur, filepath):
    """Do ETL on the log_data dataset to create the time and user dimensional table and fact table songplays"""

    # Openlog file
    df = pd.read_json(filepath, lines=True)

    # filter by NextSong action
    df = df[df['page'] == 'NextSong']

    # convert timestamp column to datetime
    t = pd.to_datetime(df['ts'], unit='ms')

    # insert time data records
    time_data = (df['ts'], t.dt.hour, t.dt.day, t.dt.week, t.dt.month, t.dt.year, t.dt.weekday)
    columns_labels = ('start_time', 'hour', 'day', 'week', 'month', 'year', 'weekday')
    time_df = pd.DataFrame(dict(zip(columns_labels, time_data)))

    for i, row in time_df.iterrows():
        cur.execute(insert_time_table, list(row))

    # Load user table
    user_df = df[['userId', 'firstName', 'lastName', 'gender', 'level']]

    # insert user records
    for i, row in user_df.iterrows():
        cur.execute(insert_users_table, row)

    # insert songplay record
    for index, row in df.iterrows():
        # get songid and artistid from song and artist tables
        results = cur.execute(song_select, (row.song, row.artist, row.length))

        songid, artistid = results if results else None, None

        # insert songplay record
        songplay_data = (row.ts, row.userID, row.level, songid, artistid, row.sessionId, row.location, row.userAgent)
        cur.execute(insert_songplay_table, songplay_data)
