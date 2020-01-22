import os
import csv
import shutil
import glob

#This script distributes all images in a given box-level directory of the Fondo Real de Cholula into
#subdirectories for each individual document. These subdirectories and their CSV files have already
#been created using Minnie's CSV split script and simple command line processes.
#Once all the files have been copied, the script updates each directory's CSV file with a manifest

firstPages = []

def copyFunction(volumen):
    destinationFolder = volumen
    with open('V:/metadata/frc/' + volumen + '_filesList.csv', 'a+', encoding='utf-8', newline='') as filesCreator:
        fileCreatorWriter = csv.writer(filesCreator, delimiter=',', quotechar='"')
        volumenList = os.listdir('V:/source/_frc/derivatives/' + volumen)
        fileCreatorWriter.writerow(volumenList)
    #Open filesList.csv and create a list of files and their identifiers 
    #for the frc_vol001 directory
    with open('V:/metadata/frc/' + volumen + '_filesList.csv', 'r+', newline='') as filesList:
        filesListWriter = csv.writer(filesList, delimiter=',', quotechar='"')
        for file in (sorted(os.listdir('V:/source/_frc/derivatives/' + volumen))): #the process requires the list of files be sorted alphabetically. Windows sometimes messes this up and this corrects it.
            identifier = file.split('.')[0]
            #print(file, identifier)
            row = [file, identifier]
            filesListWriter.writerow(row)
            
    #read master metadata file (one line per book) and skip the header row
    with open('V:/metadata/frc/frc_metadata_master_spa.csv', 'r', newline='', encoding='utf-8', errors='ignore') as masterMetadata:
        reader = csv.reader(masterMetadata, delimiter=',', quotechar='"')
        next(reader, None) #skip column headers
        for line in masterMetadata:
            firstpage = line.split(',')[0] #Read only the first column, a list of first pages. Save as 'first page'
            firstPages.append(firstpage) #Add each first page to firstPages list
    
    # Create directories, if they don't exist yet. Only needs to be run once for the whole collection!
    #for bookName in firstPages:
        #os.mkdir('V:/destination/frc_ingest/' + bookName)
        
    #Open a new CSV 'copyList' that will contain each image, its identifier, and its desination folder
    with open('V:/metadata/frc/' + volumen + '_copyList.csv', 'a+', newline='') as copyList:
        with open('V:/metadata/frc/' + volumen + '_filesList.csv', 'r+', newline='') as filesList: #open filesList, which contains the first two columns
            filesListReader = csv.reader(filesList, delimiter=',', quotechar='"')
            for fileName, fileIdentifier in filesListReader: #for each line in filesList.csv
                pageIdentifier = fileIdentifier #the identifier is column #2
                #global destinationFolder
                for line in firstPages: #for each line in the firstPages list  
                    if line == pageIdentifier: #if the firstPages list value matches the page identifier...
                        destinationFolder = line #...update the destinationFolder value to match it
                    newList = [fileName, fileIdentifier, destinationFolder] #the list for this line is the filename, file identifier, and current destinationFolder value
                writer = csv.writer(copyList, delimiter=',', quotechar='"')
                writer.writerow(newList) #write the row
                
    #Copy files from derivatives folder to destination folder
    with open('V:/metadata/frc/' + volumen + '_copyList.csv', 'r+', newline='', encoding='utf-8') as copyList:
        #copyListReader = csv.reader(copyList, delimiter=',', quotechar='"')
        for file in copyList:
            #file = file.rstrip() #strip trailing white space. This is important!
            fileName = file.split(',')[0].rstrip()
            destinationFolder = file.split(',')[2].rstrip()
            fileSource = 'V:/source/_frc/derivatives/' + volumen + '/' + fileName
            fileDestination = ('V:/destination/frc_ingest/' + destinationFolder + '/' + fileName)
            #print(fileSource, fileDestination)
            shutil.copy2(fileSource, fileDestination, follow_symlinks=True)
            
    os.remove('V:/metadata/frc/' + volumen + '_copyList.csv') #clean up your workspace!
    os.remove('V:/metadata/frc/' + volumen + '_filesList.csv')     
    
relevantExpedienteList = []

def frc_manifest(volumen):
    with open('V:/metadata/frc/frc_metadata_master_spa.csv', 'r', newline='', encoding='utf-8', errors='ignore') as masterMetadata: #open the master metadata sheet
        reader = csv.reader(masterMetadata, delimiter=',', quotechar='"')
        next(reader, None) #skip the header row
        for line in masterMetadata:
            firstPage = line.split(',')[0] #isolate the first column
            firstPageVol = firstPage[:-7] #isolate the volumen number for each expediente
            if firstPageVol == volumen:
                relevantExpedienteList.append(firstPage) #store the list of relevant expedientes

    for expediente in relevantExpedienteList:
        with open('V:/destination/frc_ingest/' + expediente +'/' + expediente + '.csv', 'a+', encoding='utf-8', newline='') as manifest: #find the CSV file for each relevant expediente
            fileWriter = csv.writer(manifest, delimiter=',', quotechar='"')
            filesList = sorted(glob.glob('V:/destination/frc_ingest/' + expediente + '/*.png', recursive=False)) #print a list of only PNG files (not the CSV itself)
            pageNum = 0 #start at page 1, which is the first page's/book's row
            #fileWriter.writerow('') #create a new row, which the splitFiles.php script doesn't do
            for file in filesList: #[1:]: #skip the first line, which is already in the manifest
                file = file.split('\\')[1] #isolate the filename from the full path
                identifier = file.split('.')[0] #isolate the identifier
                pageNum = pageNum + 1 #increase the page number counter
                #pageLabel = 'Página ' + str(pageNum) #write the page label using the page number -- UPDATE - page number labels not being used
                manifestRow = [file, identifier, pageNum] #store the filename, identifier, and page name as a list
                #print(manifestRow)
                fileWriter.writerow(manifestRow) #write the list to the row
                
user_input = input('What folder needs doing? ')
copyFunction(user_input.rstrip())
frc_manifest(user_input.rstrip())
