# Helper Functions

import csv
import os
from datetime import datetime


# Get Tag Vector for each Actor
def actor_tag_calculator(actor_id, all_tag_id):
    # Data files needed for calculating tag weights
    file_ma = os.path.join(os.pardir, "Phase2_data/movie-actor.csv")
    file_tag = os.path.join(os.pardir, "Phase2_data/mltags.csv")

    # Compute the Tag Weight that associate with Actor
    tw_dict = tag_weight_calculator(file_a=file_ma, file_b=file_tag, actor_id=actor_id)

    actor_tag_list = []

    # If Tag Weight is None
    if tw_dict is None:
        for i in range(0, len(all_tag_id)):
            actor_tag_list.append(0)
    # Else fill the weight value to relevant tag
    else:
        for i in range(0, len(all_tag_id)):
            if all_tag_id[i] in tw_dict:
                actor_tag_list.append(tw_dict.get(all_tag_id[i]))
            else:
                actor_tag_list.append(0)

    return actor_tag_list
# ----- End of Actor Tag Calculator -----


# Compute Tag Weights for each Actor
def tag_weight_calculator(file_a, file_b, actor_id):
    # Open Movie-Actor file
    with open(file_a, 'r') as fA:
        # Read Movie-Actor file
        reader_a = csv.reader(fA)
        # Skip the header
        next(reader_a, None)

        # movie_id list
        m_list = []
        # rank list
        r_list = []
        # All rank list
        all_r_list = []

        # Find all MovieIDs and Ranks associated with actor_id
        for row_a in reader_a:
            # Get all rank info
            all_r_list.append(row_a[2])

            if row_a[1] == actor_id:
                m_list.append(row_a[0])
                r_list.append(row_a[2])
    # ----- End of processing movie-actor file -----

    # If actor_id invalid or does not exist
    if len(m_list) == 0:
        print('No Result for Given Actor due to Relevant MovieID Not Found')
        return None

    # Normalize rank list to [0, 1], and map Weight(rank) to ranks
    r_dict = normalize_rank(all_r_list=all_r_list, r_list=r_list)  # dictionary for Rank : Weight(rank)

    # Process mltags file
    with open(file_b, newline='') as fB:
        # Read the mltags file
        reader_b = csv.reader(fB)
        # Skip the header
        next(reader_b, None)

        # All timestamp list
        all_ts_list = []
        # tag_id list
        t_list = []
        # timestamp list
        ts_list = []

        # Find all TagIDs and Timestamps associated with each movie_id
        for row_b in reader_b:
            # Track all timestamps
            all_ts_list.append(row_b[3])

            if row_b[1] in m_list:
                t_list.append(row_b[2])
                ts_list.append(row_b[3])

    # ----- End of processing mltags file -----

    # Normalize timestamp list to [0, 1], and map Weight(timestamp) to timestamp
    ts_dict = normalize_timestamp(all_ts_list=all_ts_list, ts_list=ts_list)

    # Open movie-actor & mltags files for total weight calculation
    with open(file_a, 'r') as fA, open(file_b, 'r') as fB:
        reader_a = csv.reader(fA)
        reader_b = csv.reader(fB)
        # Tag - Weight dictionary
        tw_dict = {}
        # For each tag - timestamp associated with one movie
        for i in range(0, len(t_list)):
            # Reset the read position of files
            fB.seek(0)
            fA.seek(0)
            # Get its Weight(timestamp) and MovieID
            m_id = 0
            for row_b in reader_b:
                if row_b[2] == t_list[i] and row_b[3] == ts_list[i]:
                    m_id = row_b[1]
                    w_ts = ts_dict.get(ts_list[i])
            # Get the associated Weight(rank)
            for row_a in reader_a:
                if row_a[1] == actor_id and row_a[0] == m_id:
                    w_r = r_dict.get(row_a[2])
            # Put or Update the combined Weight of rank and timestamp
            # If a tag already exists, update it
            if t_list[i] in tw_dict:
                # 1 stands for TF weight(tag) (raw count)
                new_w = tw_dict.get(t_list[i]) + (1 + w_ts + w_r)
                tw_dict[t_list[i]] = new_w
            else:
                # 1 stands for TF weight(tag) (raw count)
                tw_dict[t_list[i]] = 1 + w_ts + w_r

    return tw_dict
# ----- End of Tag-Weight Calculator -----


# Helper Function for Rank Normalization
def normalize_rank(all_r_list, r_list):
    # Highest value of rank
    highest = int(max(all_r_list))
    # Lowest value of rank
    lowest = int(min(all_r_list))
    difference = highest - lowest
    r_dict = {}  # dictionary for Rank : Weight(rank)
    # Normalize each rank's weight
    for r in r_list:
        r_dict[r] = (highest - int(r)) / difference

    return r_dict
# ----- End of normalize_rank -----


# Helper Function for Timestamp Normalization
def normalize_timestamp(all_ts_list, ts_list):
    # Normalize timestamp list to [0, 1], and map Weight(timestamp) to timestamp
    # Get the max and min, then give the newest timestamp 1, oldest timestamp 0
    # First convert the str into datetime
    newest = datetime.strptime(max(all_ts_list), "%Y-%m-%d %H:%M:%S")
    oldest = datetime.strptime(min(all_ts_list), "%Y-%m-%d %H:%M:%S")
    dt_difference = newest - oldest
    ts_dict = {}
    # Normalize each timestamp's weight and map them with associated timestamp
    for ts in ts_list:
        if newest != oldest:
            ts_dict[ts] = (datetime.strptime(ts, "%Y-%m-%d %H:%M:%S") - oldest) / dt_difference
        else:
            ts_dict[ts] = 1

    return ts_dict
# ----- End of normalize_timestamp -----


# Helper Function for Writing csv file
def write_csv(file_name, result_list):
    with open(file_name, 'w') as f:
        writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_ALL)

        for r in result_list:
            writer.writerow(r)
# ----- End of write_csv -----
