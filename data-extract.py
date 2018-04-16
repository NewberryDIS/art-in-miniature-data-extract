
# Note: In order for script to work:
#1) needed to find-replace all null values with ""null"" within the original presence-or-absence-classifications.csv file obtained from the Project Builder 'Data Exports'.
#2) erased all lines in original presence-or-absence-classifications.csv file prior to 2-23-17 beta launch 
# So instead of using presence-or-absence-classifications.csv, I created presence-or-absence-classifications-beta.csv that has the above changes.

# Code improvement would be to build in solutions directly for these issues

#Python 3.5.2
# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
try:
    classfile_in = sys.argv[1]
    extractfile_out = sys.argv[2]
except:
    print("\nUsage: "+sys.argv[0]+" classifications_infile extract_outfile")
    print("      classifications_infile: a Zooniverse (Panoptes) classifications data export CSV.")
    print("      markings_outfile: a CSV file with extracted information from classifications.")
    print("\nExample: "+sys.argv[0]+" test-classifications.csv test-extract.csv")
    sys.exit(0)
#classfile_in = 'presence-or-absence-classifications-beta.csv'
#extractfile_out = 'presence-or-absence-classifications-beta-extract.csv'

import pandas as pd
import json

# Read in classification CSV and expand JSON fields
classifications = pd.read_csv(classfile_in)
classifications['metadata_json'] = [json.loads(q) for q in classifications.metadata]
classifications['annotations_json'] = [json.loads(q) for q in classifications.annotations]
classifications['subject_data_json'] = [json.loads(q) for q in classifications.subject_data]

# Select only classifications from most recent workflow version
iclass = classifications[classifications.workflow_version == classifications['workflow_version'].max()]

clist=[]
i = 0
for index, c in iclass.iterrows():
	
	x = 0
	clist.append({'classification_id':c.classification_id, 'user_name':c.user_name, 'user_id':c.user_id,'created_at':c.created_at, 'subject_ids':c.subject_ids})
	
	for q in c.annotations_json[x]['value']:
		v = str(q['tool_label'])	
		for r in q['details']:
			clist[i][v] = r['value']
	x+=1			
	coverages = []
	for coverage in c.annotations_json[x]['value']:
		if 'label' in coverage:
			coverages.append(coverage['label'])
		if ('value' in coverage and coverage['value'] is not None and coverage['option']==False):
			coverages.append(coverage['value'])
	clist[i]['coverage'] = str(coverages).replace("u\"","\"").replace("u\'","\'").replace("[","").replace("]","").replace("'","").replace(", ","--")
	
	x+=1
	labels = []
	for subject in c.annotations_json[x]['value']:		
		for sv in subject['value']:			
			if 'label' in sv:				
				labels.append(sv['label'].replace(", ","*"))
			if ('value' in sv and sv['value'] is not None and sv['option']==False):
				labels.append(sv['value'])
	clist[i]['subject'] = str(labels).replace("u\"","\"").replace("u\'","\'").replace("[","").replace("]","").replace("'","").replace(",",";").replace("*",", ")
	
	x+=1
	clist[i]['orientation'] = c.annotations_json[x]['value']
	
	x+=1
	clist[i]['handwriting'] = c.annotations_json[x]['value']
	clist[i]['filename'] = str(c.subject_data_json[str(c.subject_ids)]['FILENAME']).replace(",","")
	clist[i]['filename2'] = str(c.subject_data_json[str(c.subject_ids)]['FILENAME2']).replace(",","")
	i = i+1
	

		

            
# Output list of dictionaries to pandas dataframe and export to CSV.
col_order=['classification_id','user_name','user_id','created_at','subject_ids','coverage','handwriting','orientation','subject','Postcard number','Front caption',"Artist's name or signature",'Back caption','Postmark date','filename','filename2']
out=pd.DataFrame(clist)[col_order]
out.to_csv(extractfile_out,index_label='row_id')
