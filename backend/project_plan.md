From basic PDF reader to AI past-paper analyser
1. Goal 1: Read a PDF
   - Accept a PDF upload.
   - Check that the file is valid.
   - Extract text from every page.
   - Return the extracted text and page count.
   First milestone
   Proves that our application can read past papers.
2. Goal 2: Understand the document
   - Identify the paper title, grade, subject and year where available.
   - Distinguish question papers from memorandums.
   - Identify question numbers and marks.
   - Preserve subquestion structure.
   Turns raw text into understandable exam content.
3. Goal 3: Store the information
   - Save paper details.
   - Save extracted questions.
   - Save mark allocations.
   - Prevent duplicate uploads.
   Makes the information reusable across multiple papers.
4. Goal 4: Connect questions to the curriculum
   - Define subjects and topics.
   - Map questions to the correct topics.
   - Allow uncertain mappings instead of guessing.
   - Verify the mappings.
   Gives the system educational meaning.
5. Goal 5: Analyse exam patterns
   - Count how often topics appear.
   - Calculate marks per topic.
   - Compare different exam papers.
   - Rank high-yield topics.
   Creates useful revision insights from actual exam data.
6. Goal 6: Introduce AI and RAG
   - Generate embeddings.
   - Retrieve relevant questions.
   - Answer questions using retrieved exam material.
   - Provide grounded explanations and references.
   Adds intelligent search and assistance.
7. Goal 7: Build the learner experience
   - Upload dashboard.
   - Paper and question exploration.
   - Topic rankings.
   - Revision recommendations.
   Turns the backend into a usable learner product.