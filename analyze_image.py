# Runs YOLO inference on an image, returns detected hazards and safety score of image
# # parameters are the path of the image to run inference on, and the confidence threshold to detect objects at
# def analyze_image(image_path, cthresh=0.4):
#     model = YOLO("best.pt")
#     labels = model.names
#     bbox_colors = [(164,120,87), (68,148,228), (93,97,209), (178,182,133), (88,159,106), 
#               (96,202,231), (159,124,168), (169,162,241), (98,118,150), (172,176,184)]
    
#     frame = cv2.imread(image_path)
    
#     #go through the model detections, store what was detected in a counting list
#         #2D array of each object and the "count" of each
#     results = model(frame, verbose=False, device='cpu')
    
#     #extract results (object ID, box coords, confidence scores for each object detected)
#     detections = results[0].boxes 

#     #list of class labels for bounding box labeling
#     labels = model.names 
#     # {0: 'barrel', 1: 'barrier', 2: 'debris', 3: 'log', 4: 'pothole', 5: 'pylon'}
#     # (0, 1, 5) are all = construction

#     #initialize hazard counts to 0
#     construction_count = 0
#     debris_count = 0
#     pothole_count = 0
#     log_count = 0

#     #go through each detection for one image (each "box") and return class, bbox coords, confidence
#     for i in range(len(detections)):
#         xyxy_tensor = detections[i].xyxy.cpu() # convert the detections in tensor format to CPU memory
#         xyxy = xyxy_tensor.numpy().squeeze() # convert bbox coords to a numpy array (for CPU compatability)
#         xmin, ymin, xmax, ymax = xyxy.astype(int) # store xy coords to draw box

#         classidx = int(detections[i].cls.item()) #get the class ID of the object detected
#         classname = labels[classidx]
#         confidence = detections[i].conf.item() # get the confidence score of the object detection, convert from tensor to python item

#         #count objects detected if detection confidence is > 0.4
#         if confidence > 0.4:
#             if classidx in (0,1,5):
#                 construction_count += 1
#             elif classidx == 2:
#                 debris_count += 1
#             elif classidx == 3:
#                 log_count += 1
#             elif classidx == 4:
#                 pothole_count += 1

#         counts = [construction_count, debris_count, log_count, pothole_count]

#         #draw box on object detection if confidence threshold is high enough

#         if confidence > cthresh:
#             color = bbox_colors[classidx % 10]
#             cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), color, 2)

#             label = f'{classname}: {int(confidence*100)}%'
#             labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1) # Get font size
#             label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
#             cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), color, cv2.FILLED) # Draw white box to put label text in
#             cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1) # Draw label text

        
#     #display the count of hazards in the top left of the image
#     cv2.putText(frame, f'Log Count: {log_count}',  (10,40), cv2.FONT_HERSHEY_SIMPLEX, .7, (0,255,255), 2)
#     cv2.putText(frame, f'Construction Object Count: {construction_count}',  (10,70), cv2.FONT_HERSHEY_SIMPLEX, .7, (0,255,255), 2)
#     cv2.putText(frame, f'Debris Count: {debris_count}',  (10,100), cv2.FONT_HERSHEY_SIMPLEX, .7, (0,255,255), 2)
#     cv2.putText(frame, f'Pothole Count: {pothole_count}',  (10,130), cv2.FONT_HERSHEY_SIMPLEX, .7, (0,255,255), 2)

#     #I want to be able to save the image to the edge associated with it
#     cv2.imwrite('capture.png',frame)

    
    
#     #return counts of objects and safety score of the image
#     safety_score = pothole_count*0.3 + construction_count*0.5 + debris_count*0.5 + log_count*0.6

#     return safety_score, counts 