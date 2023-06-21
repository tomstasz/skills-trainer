# skillstrainer (python 3.10)

Application useful either for recruiters or people simply trying to improve their qualifications. By default application generates quiz in the selected IT category/technology, with selected number of questions and seniority (most of the questions in the attached sqlite base are placeholders of course, but fully cappable of running locally). <br>

<p float="left">
<img src="static/images/Skillstrainer_01.png" alt="Skillstrainer" title="quiz generation process" width="100" height="100"/>
<img src="static/images/Skillstrainer_02.png" alt="Skillstrainer" title="quiz generation process" width="100" height="100"/>
<img src="static/images/Skillstrainer_03.png" alt="Skillstrainer" title="exemplary question in recruitment mode" width="100" height="100"/>
<img src="static/images/Skillstrainer_04.png" alt="Skillstrainer" title="exemplary question in training mode" width="100" height="100"/>
<img src="static/images/Skillstrainer_05.png" alt="Skillstrainer" title="correct answers in training mode" width="100" height="100"/>
<img src="static/images/Skillstrainer_06.png" alt="Skillstrainer" title="post quiz graphs" width="100" height="100"/>
</p>

Main features:
* two modes: 
  * training (displays technology and seniority of current question, as well as correct answers, as a form of instant feedback)
  * recruitment (displays only running time)
      
 * dynamic change of seniority level (if user reaches certain percentage of correct/incorrect answers, application will upgrade or downgrade seniority 
   of incoming questions on the spot)
   
 * several question types (it is possible to implement different types of questions: multichoice, open, true/false or using snippets of code/pictures as 
   options)
   
 * graphical representation of the results (in training mode besides instant feedback during quiz, application will also show results in a form of charts)
 
 * browser buttons assurance (if user tries to use browser buttons to cheat e.g. load previously answered question, application will draw the next one 
   and count current question as ommited - but still counting in final result summary)
