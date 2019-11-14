#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Chenxi Li on 2019-10-24
import csv

def construct_user_id_dict(filename, threshold):
    user_id_dict = {}
    threshold_id = []
    with open(filename, 'r') as file:
        csv_content = csv.reader(file)
        counter = 0
        for line in csv_content:
            if counter > 0 and len(line) == 3:
                user_id_dict[int(line[0])] = line[2]
                if int(line[1]) <= threshold:
                    threshold_id.append(int(line[0]))
            counter += 1
    return user_id_dict, threshold_id

def get_commentors(filename, user_id_dict, threshold_id):
    commentors = set()
    counter_commentor = set()
    with open(filename, 'r') as file:
        csv_content = csv.reader(file)
        counter = 0
        for line in csv_content:
            if counter > 0:
                if (int(line[0]) in threshold_id):
                    if int(line[1]) in user_id_dict:
                        if user_id_dict[int(line[1])] != '[deleted]':
                            commentors.add(user_id_dict[int(line[1])])
                else:
                    if int(line[1]) in user_id_dict:
                        if user_id_dict[int(line[1])] != '[deleted]':
                            counter_commentor.add(user_id_dict[int(line[1])])
            counter += 1
    return commentors, counter_commentor

def remove_duplicate(commentors, counter_commentor):
    print("============counter commentor===============")
    commentorslist = list(commentors)
    for commentor in commentorslist:
        if commentor in counter_commentor:
            commentorslist.remove(commentor)
    return commentorslist

def count_map(commentorslist, user_id_dict):
    count_dict = {}
    for commentor in commentorslist:
        counter = 0
        for user_id in user_id_dict:
            if user_id_dict[user_id] == commentor:
                counter +=1
        count_dict[commentor] = counter
    count_dict = sorted(count_dict.items(), key = lambda x:(-x[1]))
    return count_dict

def get_top_commentors(count_dict):
    top_commentors = []
    for commentor in count_dict:
        if (commentor[1] >= 10):
            top_commentors.append(commentor[0])
    print(len(top_commentors))
    return top_commentors

def generate_sybil_fake_accounts():
    accounts = []
    for i in range(1,101):
        accounts.append("fake_account_" + str(i))
    return accounts

if __name__ == '__main__':
    filename1 = "karma_nodes_5.csv"
    filename2 = 'edges_5.csv'
    user_id_dict, threshold_id = construct_user_id_dict(filename1, 1)
    commentors, counter_commentors = get_commentors(filename2, user_id_dict, threshold_id)
    commentorslist = remove_duplicate(commentors, counter_commentors)
    print(commentorslist)
    count_dict = count_map(commentorslist, user_id_dict)
    print(count_dict)
    print(get_top_commentors(count_dict))


