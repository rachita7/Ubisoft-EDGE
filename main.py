# from flask import Flask
# from flask_mongoengine import MongoEngine
# import db
from pipeline import *
from optical_flow_spell_corrector import *

# app = Flask(__name__)
# @app.route('/')
# def hello():
#     return "Hello World! I am Kiran"

# #test to insert data to the data base
# @app.route("/test")
# def test():
#     db.db.collection.insert_one({"name": "John"})
#     return "Connected to the data base!"


def run_extraction_pipeline():
    imagearray = uniqueFrames(videoUrl="./videos/TheLastofUs2Credits_Trim.mp4", isYoutubeUrl=False)
    print(len(imagearray))
    # person_names = []
    # person_names_pos = []
    for i in range(len(imagearray)):
        person_names = []
        person_names_pos = []
        ocr_detection = ocr(imagearray[i])
        if len(ocr_detection):
            draw_contour_boxes_easy_ocr(imagearray[i],ocr_detection, './contours/'+str(i)+'.jpg')
            get_person_names(person_names,person_names_pos,ocr_detection)
            person_names_pos = remove_duplicate_names(person_names_pos)
            print(person_names_pos)
            if len(person_names_pos):
                job_titles_list = get_job_titles(ocr_detection,person_names_pos)
                person_names_pos = get_final_names_pos(job_titles_list,ocr_detection)
                all_indexes = get_all_indexes(ocr_detection)
                midpoints_arr = get_midpoints(all_indexes,ocr_detection)
                kmeans_clusters = get_kmeans_clusters(job_titles_list,midpoints_arr,'k-means++')
                cluster = get_required_clusters(kmeans_clusters,5)
                all_clusters = get_all_clusters(kmeans_clusters,job_titles_list)
                nearest_names_jobs = nearest_name_to_jobtitle(job_titles_list,person_names_pos,ocr_detection)
                job_titles_dict = job_title_dict(job_titles_list)
                final_cluster = final_clusters(all_clusters,job_titles_list,nearest_names_jobs,job_titles_dict,ocr_detection)
                final_job_titles_list = get_final_job_titles_list(job_titles_dict,ocr_detection)
                print(final_job_titles_list)

# if __name__ == "__main__":
#   app.run(debug=True)
run_extraction_pipeline()