from flask_mongoengine import MongoEngine
from flask_cors import CORS
import db
from pipeline import *
from optical_flow_spell_corrector import *
from flask import Flask, request, url_for, jsonify
from flask_pymongo import PyMongo
from pymongo.errors import DuplicateKeyError
from models import *
import json
import validators
app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return "Hello World! I am Kiran"

#test to insert data to the data base
@app.route("/test")
def test():
    db.db.person.insert_one({"name": "John", 'linkedinURL':"https://www.linkedin.com/in/kiranbodipati/"})
    return "Connected to the data base!"

#--------------------------------------------------Helper Functions---------------------------------------------------------------
def run_extraction_pipeline(video="./videos/TheLastofUs2Credits_Trim.mp4", yt=False):
    imagearray = uniqueFrames(videoUrl=video, isYoutubeUrl=yt)
    print(len(imagearray))
    # person_names = []
    # person_names_pos = []
    overall_jobs_list={}
    for i in range(len(imagearray)):
        person_names = []
        person_names_pos = []
        ocr_detection = ocr(imagearray[i])
        
        if len(ocr_detection):
            draw_contour_boxes_easy_ocr(imagearray[i],ocr_detection, './contours/'+str(i)+'.jpg')
            get_person_names(person_names,person_names_pos,ocr_detection)
            person_names_pos = remove_duplicate_names(person_names_pos)
            # print(person_names_pos)
            
            if len(person_names_pos):
                job_titles_list = get_job_titles(ocr_detection,person_names_pos)
                if len(job_titles_list):
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
                    overall_jobs_list.update(final_job_titles_list)
    print(overall_jobs_list)
    return overall_jobs_list


def covert_to_person_list(job_list, company="", game="", year="", platform=""):
    overall_person_list={}
    for job in job_list.keys():
        person_list = job_list[job]
        for person in person_list:
            if person not in overall_person_list.keys():
                overall_person_list[person] =[job]
            else:
                overall_person_list[person].append(job)
    personJsonList=[]
    print(overall_person_list)
    for person in overall_person_list.keys():
        personObj={}
        personObj["name"]=person
        personObj["jobs"]=overall_person_list[person]
        personObj["company"]=company
        personObj["game"]=game
        personObj["platform"]=platform
        personObj["year"]=year
        personJsonList.append(personObj)
    print(personJsonList)
    return personJsonList

def search_linkedinUrl(name, company):
    ls = LinkedinScraper(keyword=name + " "+company,limit=25)
    ls.search()
    links = ls.parse_links()
    if len(links)==0:
        return ""
    else:
        return links[0]

#--------------------------------------------------------API Calls-----------------------------------------------------------------
@app.route("/database/vidUrl", methods=['POST'])
def get_vid_url():
    if request.method=='POST':
        data= request.get_json()
        if db.db.vidData.find_one(data):
            person_job_cursor=db.db.worksAt.find({"game":data["game"], "company":data["company"]})
            person_job_list=[]
            for doc in person_job_cursor:
                person=WorksAt(**doc)
                person = person.to_json()
                person_job_list.append(person)
            new_person_list=[]
            for person in person_job_list:
                dat =db.db.person.find_one({"name":person["name"]})
                person["linkedinURL"]=dat["linkedinURL"]
                new_person_list.append(person)
            return jsonify(new_person_list)
        else:
            if validators.url(data["url"]):
                jobList=run_extraction_pipeline(video=data["url"], yt=True)
                person_list=covert_to_person_list(jobList, company=data["company"], game=data["game"], year=data["year"], platform=data["platform"])
            new_person_list=[]
            for person in person_list:
                personWorksAt=WorksAt(**person)
                # db.db.worksAt.insert_one(personWorksAt.to_bson())
                insert_result = db.db.worksAt.insert_one(personWorksAt.to_bson())
                db.db.worksAt.id = PydanticObjectId(str(insert_result.inserted_id))
                # linkdin=search_linkedinUrl(person["name"], person["company"])
                search_string=person["name"].lower().replace(" ", "%20")+"%20"+person["company"].lower().replace(" ", "%20")
                linkdin="https://www.linkedin.com/search/results/people/?keywords="+ search_string +"&origin=GLOBAL_SEARCH_HEADER"
                person["linkedinURL"]=linkdin
                personObj={}
                personObj["name"]=person["name"]
                personObj["linkedinURL"]=linkdin 
                personmod=Person(**personObj)
                new_person_list.append(person)
                # db.db.person.insert_one(personmod.to_bson())
                insert_result = db.db.person.insert_one(personmod.to_bson())
                db.db.person.id = PydanticObjectId(str(insert_result.inserted_id))
            data=VidData(**data)
            # db.db.vidData.insert_one(data.to_bson())
            insert_result = db.db.vidData.insert_one(data.to_bson())
            db.db.vidData.id = PydanticObjectId(str(insert_result.inserted_id))
            return jsonify(new_person_list)

    

@app.route("/database/persons", methods=['GET', 'POST'])
def person_read_write():
    if request.method=='POST':
        raw_person= request.get_json()
        # raw_person =jsonify(raw_person)
        if db.db.person.find_one(raw_person):
            return("Person Exists")
        else:
            person=Person(**raw_person)
            # print(raw_person)
            insert_result = db.db.person.insert_one(person.to_bson())
            # insert_result = person.insert_one(person.to_bson())
            db.db.person.id = PydanticObjectId(str(insert_result.inserted_id))
            print("person added")
            return "person added"
    
    if request.method=='GET':
        persons_cursor = db.db.person.find({})
        person_list=[]
        for doc in persons_cursor:
            person=Person(**doc)
            person = person.to_json()
            person_list.append(person)
        return jsonify(person_list)

@app.route("/database/person", methods=['POST', 'DELETE'])
def get_delete_one_person():
    param = request.get_json()
    person = db.db.person.find_one(param)
    if person:
        if request.method=='POST':
            person=Person(**person)
            return person.to_json()
        if request.method=='DELETE':
            db.db.person.find_one_and_delete(param)
        person=Person(**person)
        return person.to_json()
    else:
        return("person does not exist")




@app.route("/database/games", methods=['GET', 'POST'])
def game_read_write():
    if request.method=='POST':
        raw_game= request.get_json()
        if db.db.game.find_one(raw_game):
            return("Game Exists")
        else:
            game=Game(**raw_game)
            insert_result = db.db.game.insert_one(game.to_bson())
            db.db.game.id = PydanticObjectId(str(insert_result.inserted_id))
            print("game added")
            return "game added"
    
    if request.method=='GET':
        game_cursor = db.db.game.find({})
        game_list=[]
        for doc in game_cursor:
            game=Game(**doc)
            game = game.to_json()
            game_list.append(game)
        return jsonify(game_list)


@app.route("/database/game", methods=['POST', 'DELETE'])
def get_delete_one_game():
    param = request.get_json()
    game = db.db.game.find_one(param)
    if game:
        if request.method=='POST':
            game=Game(**game)
            return game.to_json()
        if request.method=='DELETE':
            db.db.game.find_one_and_delete(param)
        game=Game(**game)
        return game.to_json()
    else:
        return("game does not exist")


# @app.route("/database/worksAt")
  



@app.route("/database/getJobs", methods=['GET', 'POST'])
def get_job_list():
    if request.method=='GET':
        job_cursor = db.db.worksAt.find({})
        job_list=[]
        for doc in job_cursor:
            job=WorksAt(**doc)
            job = job.to_json()
            job_list.append(job)
        new_person_list=[]
        for person in job_list:
            dat =db.db.person.find_one({"name":person["name"]})
            person["linkedinURL"]=dat["linkedinURL"]
            new_person_list.append(person)
        return jsonify(new_person_list)
    
    if request.method=='POST':
        raw_jobs= request.get_json()
        # raw_person =jsonify(raw_person)
        if db.db.worksAt.find_one(raw_jobs):
            return("data Exists")
        else:
            person=WorksAt(**raw_jobs)
            # print(raw_person)
            insert_result = db.db.worksAt.insert_one(person.to_bson())
            db.db.person.id = PydanticObjectId(str(insert_result.inserted_id))
            print("data added")
            return "data added"

#job_list={"Written By":['NEIL DRUCKMANN', 'HALLEY GROSS'], "Additional Writing":['JOSH SCHERR', 'RYAN JAMES'], "President":['NEIL DRUCKMANN']}

# covert_to_person_list(job_list)
if __name__ == "__main__":
   app.run(debug=True)
# # run_extraction_pipeline()
