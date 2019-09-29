#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Pengying Wang on 2019-09-28
import requests
import networkx as nx
import datetime


daily_query_api_prefix = "https://api.pushshift.io/reddit/submission/search/?subreddit=hongkong&"
comments_query_api_prefix = "https://api.pushshift.io/reddit/comment/search/?link_id="
author_query_api_prefix = "https://api.pushshift.io/reddit/search/comment/?author="


def query_api(date, interval, limit):
    next_day = (datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(days=interval)).strftime('%Y-%m-%d')
    request = daily_query_api_prefix + "after=" + date + "&before=" + next_day + "&limit=" + str(limit)
    # Get all the topics published in subreddit - hongkong in one day (date). in Json format
    json_data = requests.get(request).json()['data']
    # build undirected graph for user pair
    graph = nx.read_gml("user_6_7.gml")
    #graph = nx.Graph()
    id_user_dic = {}
    for data in json_data:
        user = data['author']
        graph.add_node(user)
        # link id for topic
        raw_id = data['id']
        if raw_id not in id_user_dic and user != "[deleted]":
            id_user_dic[raw_id] = user

        num_comments = data['num_comments']
        if num_comments != 0:
            build_edge(raw_id, graph, id_user_dic)
    return graph


def build_edge(link_id, graph, id_user_dic):
    parent_dic = {}
    request = comments_query_api_prefix + link_id
    json_data = requests.get(request).json()['data']
    for data in json_data:
        child_id = data['id']
        author = data['author']
        graph.add_node(author)
        if child_id not in id_user_dic and author != "[deleted]":
            id_user_dic[child_id] = author
        parent_id = data['parent_id']
        if '_' in parent_id:
            parent_id = parent_id.split("_")[1]
        if parent_id not in parent_dic:
            parent_dic[parent_id] = set()
        parent_dic[parent_id].add(child_id)
    for key, children in parent_dic.items():
        print(len(children))
        connect(children, graph, id_user_dic)
        # print("link"+child_id)
        # print("id"+data['id'])
        # id_node = Node(child_id)
        # id_node.parent = Node(data['parent_id'])
        # relation_list = [id_node]
        # while relation_list:
        #     last_level = set()
        #     #print([node.val for node in relation_list])
        #     for node in relation_list:
        #         # last_level = []
        #         if node.parent:
        #             last_level.add(node.parent)
        #     #print([node.val for node in last_level])
        #     connect(last_level, graph, id_user_dic)
        #     relation_list = last_level
    return graph


def connect(children, graph, id_user_dic):
    print("edges " + str(len(graph.edges())))
    if len(children) <= 1:
        return
    for i in children:
        for j in children:
            if i != j:
                if i in id_user_dic and j in id_user_dic:
                    user_i = id_user_dic[i]
                    user_j = id_user_dic[j]
                    graph.add_edge(user_i, user_j)
    return graph




if __name__ == '__main__':
    user_graph = query_api("2019-08-06", 30, 10000)
    nx.write_gml(user_graph,"user_6_7_8.gml")





















