/@@localroles-controlpanel
**************************
**Info**
    requires Plone4

Add or Remove local roles for objects using csv. 
The format of the csv file should be::

    path,user-/group-id,role

The data gets processed line by line. 
At the end, you'll get a notification on the number of 
successfully processed lines as well as 
verbose error notifications for each unsuccessful line. 
**Be patient!** The duration of the process depends on 
the number of lines of your csv and may take up to 
several minutes.

Example csv::

        /Plone/front-page,Reviewers,Editor
        /Plone/front-page,usera,Contributor
        /Plone/news,userb,Reviewer
        /Plone/news,userb,Editor
