import guidance

# available language models to execute guidance programs
oldAzureModel = guidance.llms.OpenAI(model="gpt-3.5-turbo",
                                     token='007dd516c49443c799524c265a87845e',
                                     api_base="https://ase-eu01.openai.azure.com/",
                                     api_type='azure',
                                     api_version="2023-03-15-preview",
                                     deployment_id='gpt-35',
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
eval = lambda x: 1 if x == "true" else 0
def calculate_score(correctness, relevance, argumentation, tone, safe, dodge):
    c = eval(correctness)
    r = eval(relevance)
    a = eval(argumentation)
    t = eval(tone)
    s = eval(safe)
    d = eval(dodge)
    print(c,r,a,t,s)
    return min(max(0, c*(2+r*2+a*2+t*2+(1-s)*2 +s*(-6) + d*6 )),10)


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

    For question: whats the implementation of binary search?
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


    {{~/system}}
    {{#assistant~}}
    {{gen 'score' temperature=0.2 max_tokens=2000}}
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

def scoring(question, answer):
    result = template2(
        question = question,
        answer = answer,
        calculate_score = calculate_score,
        llm=oldAzureModel
    )

    print(
        f"""
        Question: {question}
        Answer: {answer}
        Model score: {result['first_score']}
        Template score: {calculate_score(
            correctness=result['correctness'], 
            relevance=result['relevance'], 
            argumentation= result['argumentation'], 
            safe=result['safe'], 
            tone=result['tone'],
            dodge=result['dodge']
            )}
        Final score: {result['final_score']}
        """
    )
    return result


# question = "Hi can we add extra methods in the generalized class? Or should there only be the practice method?"
# answer = "In the context of the refactoring task, the goal is to apply the template method design pattern to the existing code. The template method pattern defines a skeleton of an algorithm in a method, which calls the hook methods in subclasses to complete the algorithm's steps. Therefore, you can add additional hook methods in the abstract base class to be implemented by concrete subclasses. However, you should avoid adding unnecessary methods that are not required by the pattern or not needed by the current implementation."


# scoring(question=question, answer=answer)

# question = "What is the best way to have multiple versions of Python on my laptop for different projects/classes?"
# answer = "Have you tried Squarspace?"


# print(scoring(question=question, answer=answer))

# question = "Verstehe ich es richtig, dass Bevorzugte Position bedeutet, wenn index von Element in Hashtable = h(x, 0) gilt?"
# answer = "Ja, das ist korrekt. Die bevorzugte Position für ein Element mit dem Schlüssel x ist der Index, der durch die Hashfunktion h(x, 0) berechnet wird."



# print(scoring(question=question, answer=answer))

# question="What is the purpose of an operating system?"
# answer="The operating system acts as an intermediary between users and hardware, managing resources and providing a platform for running applications." #[Correct]


# print(scoring(question=question, answer=answer))

# question="What is the time complexity of the binary search algorithm?"
# answer="The time complexity of binary search is O(log n) where n is the size of the input array."# [Correct]


# print(scoring(question=question, answer=answer))

# question="Can a Java program be compiled and run on any operating system?"
# answer="Yes, Java programs are platform-independent due to the Java Virtual Machine (JVM)."# [Correct]

# print(scoring(question=question, answer=answer))

# question="How many bits are in a byte?"
# answer="A byte consists of 8 bits." #[Correct]

# print(scoring(question=question, answer=answer))

# question="What is the main function of a router in a computer network?"
# answer="A router directs network traffic between different networks, allowing data packets to be transmitted efficiently."# [Correct]

# print(scoring(question=question, answer=answer))

# question="How many legs does a binary tree have?"
# answer="A binary tree does not have legs."# [False]

# print(scoring(question=question, answer=answer))

# question="Which programming language is best for machine learning?"
# answer="Assembly language." #[False]

# print(scoring(question=question, answer=answer))

# question="What is the square root of 'OpenAI'?"
# answer="Blueberry." #[Irrelevant]

# print(scoring(question=question, answer=answer))

question="How can I solve the traveling salesman problem?"
answer="Just ask nicely, and it will solve itself." #[Silly]

print(scoring(question=question, answer=answer))

question="How can I sort an array using the quicksort algorithm?"
answer="""Here is a Java implementation of the quicksort algorithm
// Quick sort implementation
public static void quickSort(int[] arr, int low, int high) {
    if (low < high) {
        int pivotIndex = partition(arr, low, high);
        quickSort(arr, low, pivotIndex - 1);
        quickSort(arr, pivotIndex + 1, high);
    }
}

// Partition the array
public static int partition(int[] arr, int low, int high) {
    int pivot = arr[high];
    int i = low - 1;
    for (int j = low; j < high; j++) {
        if (arr[j] < pivot) {
            i++;
            swap(arr, i, j);
        }
    }
    swap(arr, i + 1, high);
    return i + 1;
}

// Swap two elements in the array
public static void swap(int[] arr, int i, int j) {
    int temp = arr[i];
    arr[i] = arr[j];
    arr[j] = temp;
}
"""

print(scoring(question=question, answer=answer))

question="How many woodchuks could a wood chuck or what?"
answer="I am sorry, but as an AI assistant I am here to help you with homework related questions only."

print(scoring(question=question, answer=answer))