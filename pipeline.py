import cv2
import math
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
import easyocr
# from find_job_titles import FinderAcora
from sklearn.cluster import KMeans
import nltk
import nltk.tag.stanford as st
from utils import *

import os
java_path = "C:/Program Files/Java/jdk-14.0.2/bin/java.exe"
os.environ['JAVAHOME'] = java_path

tagger = st.StanfordNERTagger('E:/NTU course material/edge/ubisoft/Stanford-nlp-java/english.all.3class.distsim.crf.ser.gz', 'E:/NTU course material/edge/ubisoft/Stanford-nlp-java/stanford-ner.jar')
reader = easyocr.Reader(['en'])

# a = reader.readtext(Image.open('/Users/abhishekvaidyanathan/Downloads/Image1.jpg'))
def ocr(imagearray):
    # return reader.readtext(Image.open(filename))
    return reader.readtext(imagearray)

def draw_contour_boxes_easy_ocr(image, contour_boxes, write_loc):
    # image = cv2.imread(filename)
    for contours in contour_boxes:
        image = cv2.rectangle(image, (int(contours[0][0][0]), int(contours[0][0][1])), (int(contours[0][1][0]-contours[0][0][0])+int(contours[0][0][0]), int(contours[0][2][1]-contours[0][0][1])+int(contours[0][0][1])), (0, 255, 0), 2)
    plt.imshow(image)
    cv2.imwrite(write_loc,image)

def get_person_names(person_names, person_names_pos, ocr_detection):
    i = 0
    for names in ocr_detection:
        for sent in nltk.sent_tokenize(names[1]):
            tokens = nltk.tokenize.word_tokenize(sent)
            tags = tagger.tag(tokens)
            for tag in tags:
                if(tag[1] == 'PERSON'):
                    print(tag)
                    person_names.append(tags)
                    person_names_pos.append(i)
                    
        i = i+1

def remove_duplicate_names(person_names_pos):
    person_names_pos_set = set(person_names_pos)
    person_names_pos = list(person_names_pos_set)
    return person_names_pos

def get_job_titles(ocr_detection, person_names_pos):
    job_titles_list = []
    for i in range(len(ocr_detection)):
        job_titles_list.append(i)
    job_titles_list = list(set(job_titles_list)^set(person_names_pos))
    # return job_titles_list

    for x in job_titles_list:
        ls = LinkedinScraper(keyword=ocr_detection[x][1],limit=5)
        ls.search()
        person = ls.parse_people()
        sep = '-'
        stripped = person[0].split(sep, 1)[0]
        if ocr_detection[x][1].upper() in stripped.upper():
            print("test " +ocr_detection[x][1].upper())
            job_titles_list.remove(x)
    return job_titles_list

def get_final_names_pos(job_titles_list,ocr_detection):
    person_names = []
    for i in range(len(ocr_detection)):
        person_names.append(i)
    person_names = list(set(person_names)^set(job_titles_list))
    return person_names

def get_all_indexes(ocr_detection):
    total = []
    for i in range(len(ocr_detection)):
        total.append(i)
    return total

def get_midpoints(total, ocr_detection):
    midpoint_list = []
    for persons in total:
        coordinates = ocr_detection[persons][0]
        midpoint = [abs(coordinates[0][0]+coordinates[1][0])/2, abs(coordinates[0][1]+coordinates[2][1])/2]
        midpoint_list.append(midpoint)
    midpoints_arr = np.array(midpoint_list)
    return midpoints_arr

def get_kmeans_clusters(job_titles_list, midpoints_arr, init_method='k-means++'):
    # print(midpoints_arr)
    return KMeans(n_clusters=len(job_titles_list), init=init_method).fit_predict(midpoints_arr)

def get_required_clusters(kmeans_clusters, cluster_number):
    j = 0
    cluster = []
    for i in kmeans_clusters:
        if i==cluster_number:
            cluster.append(j)
        j=j+1
    return cluster

def get_all_elements_cluster(cluster,ocr_detection):
    cluster_elements = []
    for i in cluster:
        # print(ocr_detection[i][1])
        cluster_elements.append(ocr_detection[i])
        return cluster_elements

def get_all_clusters(kmeans_clusters,job_titles_list):
    cluster_final = []
    job_exists = False
    for j in range(len(job_titles_list)):
        required_cluster=[]
        required_cluster=get_required_clusters(kmeans_clusters, j)
        cluster_final.append(required_cluster)
    return cluster_final

def nearest_name_to_jobtitle(job_list, person_list,ocr_detection):
    nearest_person_list = []
    midpoint_list = []
    nearest_list = []

    for job_index in job_list: #iterating through a list of job indexes based on the ocr_detection list corrdinates
        
        nearest_person_dist = 99999999
        nearest_person_index = 0 
        nearest_person_midpoint = []

        job = ocr_detection[job_index] #getting the coordinates, text and confidence for each job title extracted by easyocr
        job_coordinates = job[0] #has 4 lists: a,b,c,d; each of which has separate x and y coordinates
        midpoint_job = [abs(job_coordinates[0][0]+job_coordinates[1][0])/2, abs(job_coordinates[0][1]+job_coordinates[2][1])/2]

        for person_index in person_list:
            
            person = ocr_detection[person_index] #getting the coordinates, text and confidence for each job title extracted by easyocr
            person_coordinates = person[0] #has 4 lists: a,b,c,d; each of which has separate x and y coordinates
            midpoint_person = [abs(person_coordinates[0][0]+person_coordinates[1][0])/2, abs(person_coordinates[0][1]+person_coordinates[2][1])/2]

            dist_job_person = math.dist(midpoint_job, midpoint_person)
            if(dist_job_person < nearest_person_dist):

                nearest_person_dist = dist_job_person
                nearest_person_index = person_index
                nearest_person_midpoint = midpoint_person
            
        nearest_person_list.append(nearest_person_index)
        midpoint_list.append(nearest_person_midpoint)
    nearest_list.append(nearest_person_list)
    nearest_list.append(midpoint_list)
    return nearest_list

def find_nearest_name(name,ocr_detection,nearest_names_jobs):
    coordinates = ocr_detection[name][0]
    nearest_name = 'Control Variable'
    min_dist = 100000
    a = 0
    b = 0
    a = abs(coordinates[0][0]+coordinates[1][0])/2
    b = abs(coordinates[0][1]+coordinates[2][1])/2
    midpoint = []
    midpoint.append(a)
    midpoint.append(b)
    for names in range(len(nearest_names_jobs[0])):
        if (name!=nearest_names_jobs[0][names]):
            dist = abs(nearest_names_jobs[1][names][1] - midpoint[1])
            if(dist<min_dist):
                nearest_name = nearest_names_jobs[0][names]
                min_dist = dist
    return nearest_name

def job_title_dict(job_titles_list):
    job_titles_dict = {}
    for jobs in job_titles_list:
        job_titles_dict[jobs] = []
    return job_titles_dict

def final_clusters(cluster_final,job_titles_list,nearest_names_jobs,job_titles_dict,ocr_detection):
    for cluster in cluster_final:
        control_job = 'control variable'
        if (cluster[0] not in job_titles_list):
            if(cluster[0] in nearest_names_jobs[0]):
                l = 0
                for j in nearest_names_jobs[0]:
                    if(j == cluster[0]):
                        job_titles_dict[job_titles_list[l]].append(cluster[0])
                        control_job = job_titles_list[l]
                        break
                    l = l+1
            else:
                a = find_nearest_name(cluster[0],ocr_detection,nearest_names_jobs)
                k = 0
                for j in nearest_names_jobs[0]:
                    if(j == a):
                        job_titles_dict[job_titles_list[k]].append(cluster[0])
                        control_job = job_titles_list[k]
                        break
                    k = k+1
        else:
            control_job = cluster[0]

        for i in range(1,len(cluster)):
            if(cluster[i] not in (nearest_names_jobs[0] and job_titles_list)):
                job_titles_dict[control_job].append(cluster[i])
            elif(cluster[i] in job_titles_list):
                control_job = cluster[i]
            else:
                l = 0
                for j in nearest_names_jobs[0]:
                    if(j == i):
                        job_titles_dict[job_titles_list[l]].append(cluster[0])
                        control_job = job_titles_list[l]
                        break
                    l = l+1

def get_final_job_titles_list(job_titles_dict,ocr_detection):
    final_job_titles_list = {}
    for i in job_titles_dict:
        final_job_titles_list[ocr_detection[i][1]] = []
        for j in job_titles_dict[i]:
            final_job_titles_list[ocr_detection[i][1]].append(ocr_detection[j][1])
    return final_job_titles_list