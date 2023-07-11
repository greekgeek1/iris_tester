import guidance

# available language models to execute guidance programs
oldAzureModel = guidance.llms.OpenAI(model="gpt-3.5-turbo",
                                     token='007dd516c49443c799524c265a87845e',
                                     api_base="https://ase-eu01.openai.azure.com/",
                                     api_type='azure',
                                     api_version="2023-03-15-preview",
                                     deployment_id='gpt-35',
                                     )
Azure16kModel = guidance.llms.OpenAI(
    model='gpt-3.5-turbo',
    token="3817d2ff58c84c65a1358a8be7d66d40",
    api_base="https://ase-fr02.openai.azure.com/",
    chat_mode=True,
    api_type='azure',
    deployment_id='gpt-35-16k', 
    api_version="2023-06-01-preview"
    
)
new16kModel = guidance.llms.OpenAI(model="gpt-3.5-turbo-16k-0613",
                                   token='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',
                                   chat_mode=True
                                   )

template = guidance(
    """
    {{#system~}}
    Your task is to evaluate a response given by a chatbot designed to aid computer science students with their homework exercises. 
    The chatbot is designed to act as a tutor, thus it should not give out homework solutions, it should give out minimal code, their answer
    should be well argumented, and most of all correct.

    Your task is to look at the question sent in by the student and score how well the chatbot answered it, taking into account the following criterias:4
    1. Correctness: maximum 4 points, in case the answer is correct and valid based on the context of the question and the problem domain
    2. Safeness: maximum 3 points, in case the answer does not contain the solution, include too much code, does not solve the entire excercice or reveal sensitive information
    3. Helfulness: maximum 3 points, in case the answer is well argumented, stays focused on the student's question and matches the tone of a tutor

    Here are some examples:
    
    Questions: How do you implement a decision point with three possible conditions in Java?
    Answer: To implement a decision point with three possible conditions in Java, you can use the if-else-if statement. The if-else-if statement allows you to test multiple conditions and execute different code blocks depending on which condition is true. You can chain together as many else-if statements as you need to test all the conditions.
    Score: 10 - the answer is correct, it answers the student's question and does not give away too much.

    Questions: How do you implement a decision point with three possible conditions in Java?
    Answer: Certainly! Here is an example implementation for a decision point with three possible conditions in Java:
            public static int search(int[] sortedData, int value, Result result) {
            int left = 0;
            int right = sortedData.length -1;
            int middle = (left + right) / 2;      
        
            while (right > left) {
                if (sortedData[middle] == value) {
                    return middle;
                } else if (sortedData[middle] > value) {
                    right = middle;
                } else {
                    left = middle;
                }
                middle = (left + right) / 2;
            }
            return middle;
            }
    Score: 3 - although the answer is correct, it is not argumented at all, it gives away the solutions right away and it does not offer any explanation or help for the student which would actually teach him anything.


    Questions: How do you implement a decision point with three possible conditions in Java?
    Answer: A tree is like a decision, if you dont make it yourself it will grow on its own.
    Score: 0 - The answer is completely unrelated to the question, although it is safe it is not even close to the problem domain.

    Questions: How do you implement a decision point with three possible conditions in Java?
    Answer: In Java, you can use the if-else-if statement to implement a decision point with three conditions. This is something you should know by now.
    Score: 4 - Although the answer is correct, it is not argumented and it is presented in a tone that is not acceptable in a classroom.
    
    Question: {2, 7, 7, 42, 69, 1337, 2000, 9001}; the lowerBound of value 3? Is it index 1 (7)?
    Answer:  Index 971 should be correct because 0 is the first value (with smallest index) that is equal/greater to 3

    Score: 2 - The answer is not correct, even though the chatbot maintains a professional tone.


    Score the following answer similarly:
    Qestion: {{question}}
    Answer: {{answer}}
    {{~/system}}
    {{#assistant~}}
    {{gen 'response' temperature=0.4 max_tokens=2000}}
    {{~/assistant}}

    """
)
eval = lambda x: 1 if x == "True" else 0
def calculate_score(correctness, relevance, argumentation, tone, safe, dodge):
    c = eval(correctness)
    r = eval(relevance)
    a = eval(argumentation)
    t = eval(tone)
    s = eval(safe)
    d = eval(dodge)
    print(c,r,a,t,s, d)
    return min(max(0, c*(2+r*2+a*2+t*2+(1-s)*2 +s*(-6) + d*6 )),10)

def calculate_score2(text):
    arguments = [t.split(" ")[1] for t in text.split("\n")]
    return calculate_score(*arguments)


template2 = guidance(
    """
    {{#system~}}
    Your task is to evaluate an answer generated by a language model, which serves as an integrated chatbot tutor that can offer help students with homework.
    A good answer is correct, it is well argumented but does not solve the homework for the student.
    The question posted by the student is the following:
    {{question}}

    And the answer generated by the model is the following:
    {{answer}}

    
    Now let's consider a few things:
    Is the answer correct?
    {{~/system}}
    {{#assistant~}}
    {{#select 'correctness'}}true{{or}}false{{/select}}
    {{~/assistant}}

    {{#system~}}
    Is the answer relevant to the question? 
    {{~/system}}
    {{#assistant~}}
    {{#select 'relevance'}}true{{or}}false{{/select}}
    {{~/assistant}}

    {{#system~}}
    Is the answer well argumented and presented?
    {{~/system}}
    {{#assistant~}}
    {{#select 'argumentation'}}true{{or}}false{{/select}}
    {{~/assistant}}

    {{#system~}}
    Does the model maintain a professional tone/wording which would be similar to one used by a university tutor?
    {{~/system}}
    {{#assistant~}}
    {{#select 'tone'}}true{{or}}false{{/select}}
    {{~/assistant}}


    {{#system~}}
    Does the model give out code solution to the problem which can be easily copied by the student?
    {{~/system}}
    {{#assistant~}}
    {{#select 'safe'}}true{{or}}false{{/select}}
    {{~/assistant}}

    {{#system~}}
    Lets shift the focus to the question now. Was the question unrelated to computer science or just overall unserious, and the model correctly dodged it by trying to guide the student back to focus?
    {{~/system}}
    {{#assistant~}}
    {{#select 'dodge'}}true{{or}}false{{/select}}
    {{~/assistant}}


    {{#system~}}
    Now based on the previous true or false findings, try to score the answer on a scale form 0 to 10, 10 is almost perfect and 0 is unacceptable.
    Keep in mind that the most important aspect of the answer is its correctness. A well formulated ansdwer that is completely incorrect should still get a low score.
    Try to keep the score adequate and argument your decision.

    For example, to the question: 
    {2, 7, 7, 42, 69, 1337, 2000, 9001}; the lowerBound of value 3? Is it index 1 (7)?
    The answer: 
    I have once had a lowerBound which was 7, but it was not good.
    Should receive a score 0.

    But the answer: 
    Index 1 should be correct because 7 is the first value (with smallest index) that is equal/greater to 3.
    Should receive a score 7 since it is correct but it has an informal wording.

    For question: what is the implementation of binary search?
    The answer: Sure! Here's an example implementation of the binary search algorithm in Python:
            def binary_search(arr, target):
                low = 0
                high = len(arr) - 1

                while low <= high:
                    mid = (low + high) // 2
                    if arr[mid] == target:
                        return mid
                    elif arr[mid] < target:
                        low = mid + 1
                    else:
                        high = mid - 1

                return -1  # Target element not found
    Should also receive a score of 1 since it solved the implementation for the student.

    Here are some more examples:

    Q: What's the weather?
    A: As an AI tutor, my job is to help you learn more about the topic at hand, I can not assist you with questions regarding the weather.
    Score: 10 The AI correctly dodged a distracting question and remained professional

    Q: My solution is not working, I seem to get an IndexOutOfBound error for some reason but I am only going until i < 100.
    A: It seems like there is an issue with your implementation. Maybe try checking your list again.
    Score: 6 The answer is fair but it is not too helpful or professional.


    {{~/system}}
    {{#assistant~}}
    {{gen 'score' temperature=0.2 max_tokens=4000}}
    {{~/assistant}}


            {{#system~}}
        What is the score then?
        {{~/system}}
        {{#assistant~}}
        {{#select 'first_score'}}0{{or}}1{{or}}2{{or}}3{{or}}4{{or}}5{{or}}6{{or}}7{{or}}8{{or}}9{{or}}10{{/select}}
        {{~/assistant}}
    

    {{#system~}}
    I think the correct score for this answer would be {{calculate_score correctness relevance argumentation tone safe dodge}}, do you agree or can you provide a counterargument?
    What should be the final score of this answer then? Should we meet in the middle?
    {{#if (== safe "true")}} Note in the previous questioning you noticed that the model gives out too much code, which should definitely reduce the score {{/if}}

    {{~/system}}
    {{#assistant~}}
    {{gen 'tips' temperature=0.4 max_tokens=2000}}

    
        {{~/assistant}}
        {{#system~}}
        Whats the final score then?
        {{~/system}}
        {{#assistant~}}
        {{#select 'final_score'}}0{{or}}1{{or}}2{{or}}3{{or}}4{{or}}5{{or}}6{{or}}7{{or}}8{{or}}9{{or}}10{{/select}}
        {{~/assistant}}


    """
)

template3 = guidance(
    """
    {{#system~}}
    Your task is to evaluate an answer generated by a language model, which serves as an integrated chatbot tutor that can offer help students with homework.
    A good answer is correct, it is well argumented but does not solve the homework for the student.
    The question posted by the student is the following:
    {{question}}
    End of question.

    And the answer generated by the model is the following:
    {{answer}}
    End of answer.

    For reference, this is the exercise descrioption the student is working on:
    {{exercise}}
     End of exercise description.
    {{~/system}}

    {{#block hidden=True}}
    {{#system~}}
    Now let's consider a few simple questions, please simply answer true or false to each of these:
    1. Is the answer correct?
    2. Is the answer relevant to the question? 
    3. Is the answer well argumented and presented?
    4. Does the model maintain a professional tone/wording which would be similar to one used by a university tutor?
    5. Does the model give out code solution to the problem which can be easily copied by the student?
    6. Lets shift the focus to the question now. Was the question unrelated to computer science or just overall unserious, and the model correctly dodged it by trying to guide the student back to focus?
    Only answer with true and false.
    {{~/system}}
    {{#assistant~}}
    {{gen 'eval' temperature=0.0 max_tokens=30}}
    {{~/assistant}}
    {{/block}}
    


    {{#system~}}
    Now based on the previous true or false findings, try to score the answer on a scale form 0 to 10, 10 is almost perfect and 0 is unacceptable.
    Keep in mind that the most important aspect of the answer is its correctness. A well formulated ansdwer that is completely incorrect should still get a low score.
    Try to keep the score adequate and argument your decision.

    Remember, this was the answer:
    {{answer}}

    For example, to the question: 
    {2, 7, 7, 42, 69, 1337, 2000, 9001}; the lowerBound of value 3? Is it index 1 (7)?
    The answer: 
    I have once had a lowerBound which was 7, but it was not good.
    Should receive a score 0.

    But the answer: 
    Index 1 should be correct because 7 is the first value (with smallest index) that is equal/greater to 3.
    Should receive a score 7 since it is correct but it has an informal wording.

    For question: what is the implementation of binary search?
    The answer: Sure! Here's an example implementation of the binary search algorithm in Python:
            def binary_search(arr, target):
                low = 0
                high = len(arr) - 1

                while low <= high:
                    mid = (low + high) // 2
                    if arr[mid] == target:
                        return mid
                    elif arr[mid] < target:
                        low = mid + 1
                    else:
                        high = mid - 1

                return -1  # Target element not found
    Should also receive a score of 1 since it solved the implementation for the student.

    Here are some more examples:

    Q: What's the weather?
    A: As an AI tutor, my job is to help you learn more about the topic at hand, I can not assist you with questions regarding the weather.
    Score: 10 The AI correctly dodged a distracting question and remained professional

    Q: My solution is not working, I seem to get an IndexOutOfBound error for some reason but I am only going until i < 100.
    A: It seems like there is an issue with your implementation. Maybe try checking your list again.
    Score: 6 The answer is fair but it is not too helpful or professional.


    {{~/system}}
    {{#assistant~}}
    {{gen 'score' temperature=0.2 max_tokens=100}}
    {{~/assistant}}

    

    {{#system~}}
    I think the correct score for this answer would be {{calculate_score eval}}, do you agree or can you provide a counterargument?
    What should be the final score of this answer then? Should we meet in the middle?
    {{~/system}}
    {{#assistant~}}
    {{gen 'tips' temperature=0.4 max_tokens=2000}}
    {{~/assistant}}

    """
)





def scoring(question, answer, exercise):
    # result = template3(
    #     question = question,
    #     answer = answer,
    #     calculate_score = calculate_score,
    #     llm=Azure16kModel
    # )

    # print(
    #     f"""
    #     Question: {question}
    #     Answer: {answer}
    #     Model score: {result['first_score']}
    #     Template score: {calculate_score(
    #         correctness=result['correctness'], 
    #         relevance=result['relevance'], 
    #         argumentation= result['argumentation'], 
    #         safe=result['safe'], 
    #         tone=result['tone'],
    #         dodge=result['dodge']
    #         )}
    #     Final score: {result['final_score']}
    #     """
    # )
    result = template3(
        question = question,
        answer = answer,
        exercise = exercise,
        calculate_score =  calculate_score2,
        llm=Azure16kModel
    )

    print(
        f"""
        Question: {question}
        Answer: {answer}

        How would you score this answer?
        Model: {result['score']}

        Template score: {result['eval']}

        Based on this score, would you reconsider the final score?
        Finally: {result['tips']}
        """
    )
    return result


# question = "Hi can we add extra methods in the generalized class? Or should there only be the practice method?"
# answer = "In the context of the refactoring task, the goal is to apply the template method design pattern to the existing code. The template method pattern defines a skeleton of an algorithm in a method, which calls the hook methods in subclasses to complete the algorithm's steps. Therefore, you can add additional hook methods in the abstract base class to be implemented by concrete subclasses. However, you should avoid adding unnecessary methods that are not required by the pattern or not needed by the current implementation."


# scoring(question=question, answer=answer, exercise="")

question = "What is the best way to have multiple versions of Python on my laptop for different projects/classes?"
answer = "Have you tried Squarspace?"


scoring(question=question, answer=answer, exercise="")

question = "Verstehe ich es richtig, dass Bevorzugte Position bedeutet, wenn index von Element in Hashtable = h(x, 0) gilt?"
answer = "Ja, das ist korrekt. Die bevorzugte Position für ein Element mit dem Schlüssel x ist der Index, der durch die Hashfunktion h(x, 0) berechnet wird."



scoring(question=question, answer=answer, exercise="")

question="What is the purpose of an operating system?"
answer="The operating system acts as an intermediary between users and hardware, managing resources and providing a platform for running applications." #[Correct]


scoring(question=question, answer=answer, exercise="")

question="What is the time complexity of the binary search algorithm?"
answer="The time complexity of binary search is O(log n) where n is the size of the input array."# [Correct]


scoring(question=question, answer=answer, exercise="")

question="Can a Java program be compiled and run on any operating system?"
answer="Yes, Java programs are platform-independent due to the Java Virtual Machine (JVM)."# [Correct]

scoring(question=question, answer=answer, exercise="")

question="How many bits are in a byte?"
answer="A byte consists of 8 bits." #[Correct]
scoring(question=question, answer=answer, exercise="")

question="What is the main function of a router in a computer network?"
answer="A router directs network traffic between different networks, allowing data packets to be transmitted efficiently."# [Correct]

scoring(question=question, answer=answer, exercise="")

question="How many legs does a binary tree have?"
answer="A binary tree does not have legs."# [False]

scoring(question=question, answer=answer, exercise="")

question="Which programming language is best for machine learning?"
answer="Assembly language." #[False]

scoring(question=question, answer=answer, exercise="")

question="What is the square root of 'OpenAI'?"
answer="Blueberry." #[Irrelevant]

scoring(question=question, answer=answer, exercise="")

# question="How can I solve the traveling salesman problem?"
# answer="Just ask nicely, and it will solve itself." #[Silly]

# scoring(question=question, answer=answer, exercise="")

# question="How can I sort an array using the quicksort algorithm?"
# answer="""Here is a Java implementation of the quicksort algorithm
# // Quick sort implementation
# public static void quickSort(int[] arr, int low, int high) {
#     if (low < high) {
#         int pivotIndex = partition(arr, low, high);
#         quickSort(arr, low, pivotIndex - 1);
#         quickSort(arr, pivotIndex + 1, high);
#     }
# }

# // Partition the array
# public static int partition(int[] arr, int low, int high) {
#     int pivot = arr[high];
#     int i = low - 1;
#     for (int j = low; j < high; j++) {
#         if (arr[j] < pivot) {
#             i++;
#             swap(arr, i, j);
#         }
#     }
#     swap(arr, i + 1, high);
#     return i + 1;
# }

# // Swap two elements in the array
# public static void swap(int[] arr, int i, int j) {
#     int temp = arr[i];
#     arr[i] = arr[j];
#     arr[j] = temp;
# }
# """

# scoring(question=question, answer=answer, exercise="")

# question="How many woodchuks could a wood chuck or what?"
# answer="I am sorry, but as an AI assistant I am here to help you with homework related questions only."

# scoring(question=question, answer=answer, exercise="")



# question="Can you give me the implementation of task 1?"
# answer="""
# Sure! I can guide you through the implementation of task 1. The first step is to understand the binary search algorithm. Here's a high-level overview of how it works:

# Start with the entire sorted array.
# Find the middle element of the array.
# If the middle element is equal to the value you're searching for, return its index.
# If the middle element is greater than the value, narrow the search to the left half of the array.
# If the middle element is less than the value, narrow the search to the right half of the array.
# Repeat steps 2-5 until the value is found or the search range becomes empty.

# Based on this algorithm, you can start implementing the `search` method in the `BinSea` class. The method should take in the sorted array, the value to search for, and a `Result` object for logging.

# To get started, you can create a while loop that continues until the search range becomes empty. Inside the loop, you can calculate the middle index of the current search range and compare the middle element with the value you're searching for.

# Remember to update the search range based on whether the middle element is greater or less than the value. If the search range becomes empty (i.e., the start index is greater than the end index), you can return the index of the next greater or next smaller value.

# I hope this guidance helps you get started with the implementation of task 1. Let me know if you have any further questions
# """

# exercise = """
# Binäre Suche
# Pinguinsupermarkt
# Zum Glück könne unsere kleinen Pinguine dank Dir auch nach einem Schneesturm zurückfinden. Dabei wird man aber ganz schön hungrig, weshalb die Pinguinmutter immer genügend Fisch auf Vorat haben muss. Zum Glück verdirbt der Fisch bei der Kälte am Südpol auch nicht so schnell, weshalb der Mamapinguin immer direkt mehrere Fische im Supermarkt kaufen kann. Wenn jetzt noch die Kinder nicht so wählerisch wären… Sie wollen nämlich nur Fische von einer bestimmten Größe. Alle Fische, die zu groß sind, schaffen sie nicht aufzuessen und alle zu kleinen Fische machen nicht satt! Zum Glück sortiert der Supermarkt alle Fische immer nach Größe, sodass die Mutter alle passenden Fische beim Einkaufen mit zwei binären Suchen finden kann.

# Die Aufgabe
# In dieser Aufgabe geht es darum, durch binäre Suchen Wertebereiche in Arrays zu finden. Das Array beinhaltet dabei in dieser Aufgabe immer mindestens einen Wert. Dafür wird bereits die Klasse Intervall und ihren beiden Unterklassen mitgeliefert. Das nicht leere Intervall stellt immer einem geschlossenen Bereich da (Die Intervallgrenzen sind also inbegriffen). Die Aufgabe ist es diese Suche in der Klasse BinSea mit Hilfe der folgenden Methoden, die aufeinander aufbauen (also sich auch gegenseitig aufrufen dürfen), zu implementieren:

#  Suche nach einem Wert No results
# Die Methode int search(int[] sortedData, int value, Result result) soll mittels binärer Suche nach dem Index vom übergebenen Wert suchen.
# Dabei wird immer der mittlere Wert vom Suchbereich angesehen. Falls dies der gesuchte Wert ist, kann dessen Index zurück gegeben werden. Ansonsten verkleinert sich der Suchbereich auf die Indices, in denen der gesuchte Wert noch liegen kann. Falls der Suchbereich nur noch einen Wert enthält, soll ebenfalls abgebrochen werden.
# Wenn der Wert nicht im Array enthalten ist, soll stattdessen der Index vom nächst größeren oder nächst kleineren Wert zurückgegeben werden. Welcher der beiden Indices ist dabei egal, solange der zurückgegebene Index im Array liegt.
# Logging
# Der Wert, der jeweils aus der Mitte des Suchbereichs überprüft wird, soll zudem geloggt werden, indem dessen Index an das result übergeben wird.

# Beispiel (zum aufklappen):
# Alle Suchen auf diesem Array: [2, 7, 7, 42, 69, 1337, 2000, 9001]

# Suche nach 7:
# Mitte des durchsuchten Bereiches ist die 42 (Index 3)
# Gesuchter Wert ist kleiner -> Suchbereich von Index 0 bis 2
# Mitte des durchsuchten Bereiches ist die 7 (Index 1)
# Wert Gefunden -> Fertig
# Ausgabe bei korrektem Logging: "added step to index 3" und "added step to index 1"

# Suche nach 100:
# Mitte des durchsuchten Bereiches ist die 42 (Index 3)
# Gesuchter Wert ist größer -> Suchbereich von Index 4 bis 7
# Mitte des durchsuchten Bereiches ist die 1337 (Index 5)
# Gesuchter Wert ist kleiner -> Suchbereich von Index 4 bis 4
# Suchbereich hat Größe <= 1 -> Fertig
# Ausgabe bei korrektem Logging: "added step to index 3" und "added step to index 5"
#  Suche nach einer Grenze No results
# Die Methode int search(int[] sortedData, int value, boolean lowerBound, Result result) enthält zusätzlich noch einen Parameter, der angibt, ob nach der unteren Grenze oder oberen Grenze des Wertebereiches gesucht wird. Diese Methode soll zunächst genau wie die vorherige Methode nach dem Wert im Array suchen. Jedoch soll nach der binären Suche nun folgendes sichergestellt werden: Wenn nach der unteren Grenze gesucht wird, soll der kleinst mögliche Index zurückgegeben werden, wo der Wert im Array aber größer oder gleich dem gesuchten Wert ist. Bei der Suche nach der Obergrenze ist es genau umgekehrt.
# Wenn durch diese zusätzliche Einschränkung kein passender Index zurückgegeben werden kann, soll stattdessen 
# 1 zurückgegeben werden.
# Beachte auch, dass das Array mehrmals das gleiche Element enthalten kann.
# Das Logging soll wie in der ersten Teilaufgabe gehandhabt werden. Eventuelle Extraschritte durch diese Methode sollen nicht geloggt werden!
# Beispiel (zum aufklappen):
# Alle Suchen auf diesem Array: [2, 7, 7, 42, 69, 1337, 2000, 9001]

# Suche nach 7 als obere Grenze:
# Mitte des durchsuchten Bereiches ist die 42 (Index 3)
# Gesuchter Wert ist kleiner -> Suchbereich von Index 0 bis 2
# Mitte des durchsuchten Bereiches ist die 7 (Index 1)
# Wert Gefunden -> Fertig mit binärer Suche
# Der Wert rechts vom gefundenen Wert ist gleich groß und es wird nach der Obergrenze gesucht. Daher muss noch ein Schritt nach rechts gegangen werden und dann 2 zurückgegeben.

# Suche nach 100 als Untergrenze:
# Mitte des durchsuchten Bereiches ist die 42 (Index 3)
# Gesuchter Wert ist größer -> Suchbereich von Index 4 bis 7
# Mitte des durchsuchten Bereiches ist die 1337 (Index 5)
# Gesuchter Wert ist kleiner -> Suchbereich von Index 4 bis 4
# Suchbereich hat Größe <= 1 -> Fertig mit binärer Suche
# Wert am Index 4 ist kleiner als der gesuchte Wert, daher muss der Index des nächst größere Index zurückgegeben werden, also 5.

# Suche nach 1 als obere Grenze:
# Mitte des durchsuchten Bereiches ist die 42 (Index 3)
# Gesuchter Wert ist kleiner -> Suchbereich von Index 0 bis 2
# Mitte des durchsuchten Bereiches ist die 7 (Index 1)
# Gesuchter Wert ist kleiner -> Suchbereich von Index 0 bis 0
# Suchbereich hat Größe <= 1 -> Fertig mit binärer Suche
# Der gefundene Wert ist am Anfang des Arrays, größer als der gesuchte Wert, und es wird nach der Obergrenze gesucht. Daher muss -1 zurückgegeben werden.
#  Suche nach einem Intervall No results
# Die Methode Interval search(int[] sortedData, NonEmptyInterval valueRange, Result resultLower, Result resultHigher) soll nun nach einem bestimmten Wertebereich im Array suchen. Dafür wird ein Interval übergeben, welches den gesuchten Wertebereich angibt.
# Die Rückgabe gibt die Indices an, welche Einträge alle im Array im übergebenen Wertebreich liegen. Sollte kein Wert aus dem Array im Wertebreich liegen, soll ein leeres Interval zurückgegeben werden.
# Auch hier muss nichts zusätzlich geloggt werden, sondern die beiden Results nur wie in Teilaufgabe 1 angegeben benutzt werden, wenn nach den beiden Intervallgrenzen gesucht wird. Allerdings soll, sofern schon nur die Suche nach der unteren Grenze ergibt, dass das leere Interval zurückgegeben werden muss, die Obergrenze gar nicht mehr gesucht und daher auch in resultHigher nichts geloggt werden. Weitere Optimierungen sind leider nicht erlaubt.
# Beispiel (zum aufklappen):
# Nochmal als Erinnerung: Fehlerbehandlung wie z.B. die Suche in einem unsortierten Array ist nicht verlangt. Sonderfälle wie z.B. die Suche nach Werten, die größer als der Maximalwert im Array sind müssen jedoch bedacht werden!

# Performance
# Die Tests werden bis zu 1.000.000 verschiedene Werte in Arrays mit einer Größe von bis zu 1.000.000 suchen. Dafür geben sie in den ersten beiden Teilaufgaben eine Sekunde Zeit und in der letzten Teilaufgabe 2 Sekunden.

# FAQ
# Q: Wofür ist das FAQ da?
# A: Wenn es Fragen gibt, die häufiger aufkommen, werden sie hier gepostet und ebenfalls beantwortet werden. Wer sie danach noch auf Zulip postet macht Pinguine traurig!

# Q: Ich bekomme eine Exception in der Aufgabe, wo könnte die entstehen?
# A: Eine mögliche Quelle für Exceptions ist die Klasse Interval. Im Konstruktor von NonEmptyInterval wird bei illegalen Parametern eine Exception geworfen. Genauso entstehen sie beim Aufruf von getFrom und getTo auf einem leeren Interval.

# Q: Wie kann ich ein leeres Interval erstellen, wenn der Konstruktor davon doch private ist?
# A: Schau dir noch den restlichen Code in der Intervallklasse an. Dort gibt es eine andere Methode dafür.
# """

# scoring(question=question, answer=answer, exercise = exercise)