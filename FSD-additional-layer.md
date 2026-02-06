#### Feature/additional-layer FSD

The feature request is to add additional layer to the application. There is couple of things that we will need to figure out and make a decision about. Here is the rundown of what a workflow for admin / coach will be.

The app is initially setup with only the basic set of questions. Which are the questions for categories 0 - 12 where category 0 is the center of the wheel one, which will not have additional layer since it's center one surrounded by the cateogires 1-12 check SVG files.

When needed the coaches / admins can add additional layer of questions for categories 1-12. And with those additional questions existing they should be able to switch between base questions and layer 1, years in layer 2 etc. Which will either show wheel with one additional layer of questions or two additional layers of questions.

When taling about layer I mean +4 questions for each layer. So to lay it down:
- base wheel has categories 0-12 where each of those have 4 questions. Therefore 13 * 4 questions.
- layer 1 will add 4 addtional questions for categories 1-12 there fore it will be 13 * 4 + 12 * 4 questions in total

And so on... But let's now focus on layer 2.

##### Considerations

There are couple of things that will need to be resolved as we implmeent this.

###### Layer reordering and questoin edits

As for now, the questions and categories are separate from the assessments. Basically because of this reorganization option / feature and fact that questions can be modified at any point, we are creating snapshot of current questions, categories and their order for each created assessment so that answers from teams will match the questions and won't get skewed or mixed when questions or order of categories changes.

We need to keep that in mind. And probably disable the reogranization of the 0th layer. Since that is the only one who will always only have 4 questions and no more.

Maybe there is more to keep in mind about that.

###### Extend existing assessments for extra questions

From the UI perspective there needs to be way for coaches or admins to say... This team filled the assessment and we need to learn more about them. Let's set their assessment to use layer 1 wheel. Which will ultimately show the additional questions to the team so that they can go through it and answer them.

Problem is that snapshot of questions is created when Assessment is created. When we will add this feature, the existing assessment will not include snapshot of layer 1 questions but only the base layer. So we need to make sure that database will handle it properly.

The UI of setting the assessments layer status should be on both:
1) creation of the assessment in case that layer 1 questions are fully popuplated
2) settings page, dropdown of assessments after they have been already created.

###### Reports and other placements of wheel

There is a review feature that provides list type of view for all the questions and answers for coaches as well as reporting feature that stores snapshot of the SVG. We need to make sure that when creating / showing those pages. Corrent SVG wheel is shown based on what layer is unlocked for given assessment.

###### Editting

There needs to be UI for admins / coaches to be able to add new questions to the layer 1. Potentially to layer 2 etc. 

##### Answers for developemnt

There are some answers for initial rundown of the evaluation:

###### DB storage of layer question

Questions in layer should be stored within the same table as the questions table. The currently the questions are stored by indexing them from 1-4. Where the addiional layers just hould use indexing that exceeds that meaning 5-8 for layer 1 then in future if needed we will use 9-12 for layer 2 etc. Which will make it easier for rendering and wheel file decision making. Just check for what layer is allowed and pick the SVG with 4 8 12 layers of questoins...

Previous mention of assessments_questions was mistake. DB storage for layer 1 questions as well as base layer questions should be the questions table.

We should not use additional columns. just use where with ranges while querying.

In assessment table we probably will need additional column for layer_enabled = 0 base, 1 for base + layer 1, 2 for base + layer 1 and 2 and so on...


###### Workflow of adding questions

It would be good for coach to be able to add questions one at the time. But maybe we should prevent him from assigning the layer 1 questions to assessment unless all questions are filled in? To prevent poor user experiance?

Thinking about it, since there will be 12 * 4 new questions 48. With the base layer 13 * 4 = 52 questions. We really should have some sort of bulk question upload option maybe CSV should be the one?

Generate some mass upload / update mechanism. Where we offer sample CSV file with all required fields that someone can download. Edit and reulpoad with some warning that reupload will replace all existing questions?

###### Snapshot of current questions

Since the layer 1, 2,... questions can be added at any point, it really doesn't make sense to create snapshot of those additional layers in moment assessment is created. We should probably create the snapshot when the layer is extended. So... following up on adding / editting questions one by one. Unless all questions for layer are in. You shoudn't be able to create or extend existing assessment to layer 1, 2,.... So Layer 1 questions should be snapshotted in moment of upgrading the assessment rather than on creation.

###### Answers when assessment is downgraded

This is tricky one... We should probably do both options. When downgrade detected, we should offer option for deleting all layer questions & answers or keeping them in.

The downgrade should be modal confirmation. So just ask user if he want's to just hide the data from user or delete them from the asssessment all together. With deleting alltogether should be double verified, with are you sure? Warning that all additional data will be lost, Qs and Answers... Default should be to keep the data for sure. We can delete them at anypoint.

Also when the data are just hidden... There should be change in UI for the option to delete it alltogether if needed. So that they woudn't have to enable, hide / delete again.

###### Wheel visualization with new layers

I will create new SVG for layer 1 at this point which will provide spots for layer 1 questions of categories 1-12.

Category 0 will stay at 4 questions!

###### Mid assessment upgrade

When assessments are upgraded mid way through filling them, since we are using server side rendering. The next answer they answer after the switch happend should render the wheel with addiional layer. Just follow what is stored at the assessment. Nothing like... Oh you haven't finished let's store your progress and not show you the next layer till you click thorugh the last. Nope, if at one point they are answering question for base assessment, and coach updates it, next click they will see the bigger wheel.

###### Progress indicatior issue

We don't have anything like progress indicator, but if we would... Then again... answered number of Qs / available numer of Qs, so if base layer than we divide by base number of questoins...

###### Reoredering with layer 1,2,...

Yes layer 0 will be forzen as layer 0... The rest shoudn't really matter. all questions will just change their order.

###### Admin deleting layer 1 questions after snapshotted assessment existing.

If assessment has questions snapshotted before deletion, those questions will stay with the assessment, ignoring whether or not the questions in instance for layer 1 exists or not. If the coach degrades the assessmetn from layer 1 to base, and are offered to: keep / delete all answers and questions from that assessment layer 1, and selects delete, then and only then the questions and answers will be lost forever.

Which again count's even for moving questions around. As long as they are snapshoted in the assessment the admin chagnign things doesn't od anything to the assessment unless the layer 1 stuff is deleted. Then if updated back to layer 1 with new questions than new questions will be popuplated.

If data are kept, not deleted from assessmetnt's layer 1, than downgrading and reupgrading should show the existing data that stayed in db.

###### Overlapping asssessments feature

Overlapping assessments... Let's deal with that later... There are still some back and forth about this fature going on.

###### Reports/Reviews

Reports when created should use current version of assessment. When upgraded the layer 1 including svg with fields etc. for it should be present.

