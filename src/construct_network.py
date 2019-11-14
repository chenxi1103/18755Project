#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Chenxi Li on 2019-09-26
import requests
import csv
import datetime

daily_query_api_prefix = "https://api.pushshift.io/reddit/submission/search/?subreddit=hongkong&"
comments_query_api_prefix = "https://api.pushshift.io/reddit/comment/search/?link_id="
class reddit_item:
    def __init__(self, user_name, karma, id):
        self.user_name = user_name
        self.karma = karma
        self.id = id


def query_api(date, interval, limit):
    next_day = (datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(days=interval)).strftime('%Y-%m-%d')
    request = daily_query_api_prefix + "after=" + date + "&before=" + next_day + "&limit=" + str(limit)
    # Get all the topics published in subreddit - hongkong in one day (date). in Json format
    json_data = requests.get(request).json()['data']

    # Construct a dict for storing parent-child relationship (id-id pair)
    relationship_dict = {}
    # Construct a dict for storing id-score relationship (id - karma pair)
    karma_dict = {}

    for data in json_data:
        id = data['id']
        user_name = data['author']
        score = data['score']
        reddit = reddit_item(user_name, score, id)

        if id not in relationship_dict:
            relationship_dict[id] = []
        if id not in karma_dict:
            karma_dict[id] = reddit
        num_comments = data['num_comments']
        if num_comments != 0:
            query_comments(id, relationship_dict, karma_dict)

    return relationship_dict, karma_dict


def query_comments(link_id, relationship_dict, karma_dict):
    request = comments_query_api_prefix + link_id
    try:
        if requests.get(request).json() is not None:
            json_data = requests.get(request).json()['data']
            for data in json_data:
                id = data['id']
                score = data['score']
                user_name = data['author']
                parent_id = data['parent_id']

                if "_" in parent_id:
                    parent_id = parent_id.split("_")[1]
                if parent_id not in relationship_dict:
                    relationship_dict[parent_id] = []
                relationship_dict[parent_id].append(id)
                karma_dict[id] = reddit_item(user_name, score, id)
    except:
        pass


def write_edges_to_file(file_name, relationship_dict, node_dict):
    with open(file_name, 'w') as file:
        csv_write = csv.writer(file)
        csv_head = ["Source", "Target"]
        csv_write.writerow(csv_head)
        for parent in relationship_dict:
            children = relationship_dict[parent]
            if len(children) > 0:
                for child in children:
                    data_row = []
                    data_row.append(node_dict[parent])
                    data_row.append(node_dict[child])
                    csv_write.writerow(data_row)


def write_karma_edges_to_file(file_name, relationship_dict, karma_dict):
    with open(file_name, 'w') as file:
        csv_write = csv.writer(file)
        csv_head = ["Source", "Target", "user_name"]
        csv_write.writerow(csv_head)
        for parent in relationship_dict:
            children = relationship_dict[parent]
            if len(children) > 0:
                for child in children:
                    data_row = []
                    if parent not in karma_dict:
                        data_row.append(-1)
                    else:
                        data_row.append(karma_dict[parent].score)

                    if child not in karma_dict:
                        data_row.append(-1)
                    else:
                        data_row.append(karma_dict[child].score)
                        data_row.append(karma_dict[child].user_name)
                        data_row.append(karma_dict[child].user_full_name)
                    csv_write.writerow(data_row)


def write_id_node_to_file(file_name, node_dict):
    with open(file_name, 'w') as file:
        csv_write = csv.writer(file)
        csv_head = ["id", "label"]
        csv_write.writerow(csv_head)
        for node in node_dict:
            data_row = []
            data_row.append(node_dict[node])
            data_row.append(node)
            csv_write.writerow(data_row)


def write_karma_node_to_file(file_name, node_dict, karma_dict):
    with open(file_name, 'w') as file:
        csv_write = csv.writer(file)
        csv_head = ["id", "karma", "author"]
        csv_write.writerow(csv_head)
        for node in node_dict:
            data_row = []
            data_row.append(node_dict[node])
            if node not in karma_dict:
                data_row.append(-1)
            else:
                if karma_dict[node].karma is not None:
                    data_row.append(karma_dict[node].karma)
                else:
                    data_row.append(-1)
                if karma_dict[node].user_name is not None:
                    data_row.append(karma_dict[node].user_name)
            csv_write.writerow(data_row)


def generate_node_dict(relationship_dict):
    dict = {}
    counter = 0
    for node in relationship_dict:
        if node not in dict:
            dict[node] = counter
            counter = counter + 1
        if len(relationship_dict[node]) > 0:
            for child in relationship_dict[node]:
                if child not in dict:
                    dict[child] = counter
                    counter = counter + 1
    return dict


if __name__ == '__main__':
    relationship_dict, karma_dict = query_api("2019-11-01", 30, 10000)
    node_dict = generate_node_dict(relationship_dict)
    write_id_node_to_file("id_nodes_11.csv", node_dict)
    write_karma_node_to_file("karma_nodes_11.csv", node_dict, karma_dict)
    write_edges_to_file("edges_11.csv", relationship_dict, node_dict)
