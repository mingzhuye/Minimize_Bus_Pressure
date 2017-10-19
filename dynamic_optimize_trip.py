# Find the best virtual or real campus choice for each student to minimize travel cost. 

import itertools
import csv
import sys
import time

benchmark_start_time = time.time()
print 'Start Time elapsed: ', benchmark_start_time

# Initialize maps (dictionary, list, tuple)
RUID_home = dict()
original_meeting_campus_map = dict()
original_schedule_map = dict()
vc_dict = dict()
result = dict()

# Helper function to generate 24-hour time format and meeting_id from a CSV line
def get_meeting_id(raw_line, column_ids, pam_index, start_index):
	line = list(raw_line[i] for i in column_ids)
	if None in line:
		return None
	if line[pam_index] == "P" and line[start_index][0:2] != "12":
		line[start_index] = str(1200 + int(line[start_index]))
	return "#".join(line)	
	
# Helper function to generate ruids from the original_schedule_map enrolled in the meeting of input2
def get_ruids(meeting_id, schedule_map):
	ruid_lst = list()
	for k, v in schedule_map.iteritems():
		if isinstance(v, dict):
			for inner_key, inner_value in schedule_map[k].iteritems():
				if meeting_id in inner_value:
					ruid_lst.append(k)
	return ruid_lst				

# Helper function to generate a sorted schedule list according to ruid and day
def get_sorted_schedule(ruid, day, schedule_map):
	sorted_schedule = list()
	if ruid in schedule_map.keys():
		if day in schedule_map[ruid].keys():
			schedule = schedule_map[ruid][day]
			sorted_schedule = sorted(schedule, key = lambda metid: int(metid[4:8])) 
			sorted_schedule = sorted_schedule + [sorted_schedule[0]]
	return sorted_schedule

# Helper function to get meeting_id from vc_dict
def get_campus(meeting):
	meeting =  meeting.split('#')
	real_campus = meeting[3]
	return real_campus
	
# Helper function to get original daily trip numbers for all ruids enrolled in the meeting of input2
def get_original_trip_number(ruid, sorted_schedule):
	num = 0 
	if len(sorted_schedule) <= 2: 
		return 0
	for i in range(1, len(sorted_schedule)):
		if sorted_schedule[i][9] != sorted_schedule[i-1][9]:
			num += 1
	return num

# Helper function to calculate total travel numbers for per student's virtual campus choice route
def get_trip_number(vc_choice, home):		
	virtual_route = [home] + list(vc_choice) + [home]
	if len(virtual_route) <= 2:
		return 0
	num = 0	
	for i in range(1, len(virtual_route )):
		if virtual_route[i] != virtual_route[i-1]:
			num +=1
	return num			

# Helper function to optimize trip numbers for each ruid from virtual campus list
def optimize(schedule, vc_dict, home):
	ordered_vc_list = list()
	for meeting in schedule:
		if meeting in vc_dict:
			ordered_vc_list.append(vc_dict[meeting])
		else:
			ordered_vc_list.append([get_campus(meeting)])
	vc_choice = min(itertools.product(*ordered_vc_list), key=lambda x: get_trip_number(x, home))
	return (get_trip_number(vc_choice,home), vc_choice)

# Read in the raw CSV file to generate RUID_home, original_meeting_campus_map, original_schedule_map
with open(sys.argv[1], 'rb') as f:
	reader = csv.reader(f, delimiter=',')
	next(reader)
	for line in reader:
		ruid = line[0]
		day = line[1]
		campus = line[5]
		meeting_id = get_meeting_id(line, [1, 2, 3, 5, 6, 7], 1, 2)
		# RUID_home	dictionary
		if line[7] == 'ROOM':
			RUID_home[ruid]= line[5]	
		# Generate original_meeting_campus_map		
		original_meeting_campus_map[meeting_id] = campus
		# Generate original_schedule_map
		if ruid not in original_schedule_map:
			original_schedule_map[ruid] = dict()
		if day not in original_schedule_map[ruid]:
			original_schedule_map[ruid][day] = list()
		original_schedule_map[ruid][day].append(meeting_id) 
		
# Read in the user modification CSV file to generate the virtual choice dictionary 'vc_dict'
# Calculate total saved trips for meetings in input2
with open(sys.argv[2], 'rb') as f:
	reader = csv.reader(f, delimiter=',')
	next(reader)
	total_saved_trip = 0 #
	for line in reader: 
		day = line[0]
		meeting_id = get_meeting_id(line, [0, 1, 2, 3, 4, 5], 1, 2)
		if len(line) is 0:
			continue
		if meeting_id not in original_meeting_campus_map.keys(): 
			print (meeting_id + " doesn\'t exist") 
			continue	
		vc = list(line[i] for i in [3,6,7])
		vc_dict[meeting_id] = vc
		ruids = get_ruids(meeting_id, original_schedule_map)
		result[meeting_id] = list()	
		meeting_saved_trip = 0 #
		for ruid in ruids:
			sorted_schedule = get_sorted_schedule(ruid, day, original_schedule_map)
			(optimized_trip_num, vc_choice) = optimize(sorted_schedule, vc_dict, RUID_home[ruid])
			original_trip_num = get_original_trip_number(ruid, sorted_schedule)
			person_saved_trip = original_trip_num - optimized_trip_num
			result[meeting_id].append((ruid, sorted_schedule, original_trip_num, vc_choice, optimized_trip_num, person_saved_trip))
			meeting_saved_trip += person_saved_trip			
		print "For Meeting_ID: ", meeting_id, ", will save trips", meeting_saved_trip	
		total_saved_trip += meeting_saved_trip
	print "For all the meetings above, total saved trips: ", total_saved_trip

# Write output into the CSV file
with open('Dynamic_Optimize_Result.csv', 'w') as w:
    writer= csv.writer(w, delimiter=',')
    writer.writerow(('Meeting_ID', 'RUID', 'Sorted_Schedule', 'Original_Trip_Num', 'VC_Choice_Route', 'Optimized_Trip_Num', 'Saved_Trip_Num'))
    text = [0] * 7
    for meeting_id in result.keys():
    			for tu in result[meeting_id]:
    				lst = [meeting_id]
    				for item in tu:
    					lst.append(item)
    				text= lst
    				writer.writerow(text)

benchmark_end_time = time.time()
print 'End Time: ', benchmark_end_time
print 'Time elapsed: ', (benchmark_end_time - benchmark_start_time)