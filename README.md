### GoR Evaluation/Contribution 

Table of Contents:
- [Thought Process](#thought-process)
- [Flow](#flow)

#### Thought Process
@MichaelFrazzy and I have been in discussions about how we can progress the scoring of contributions. As a very early and initial version, we’ve put together a basic script that pulls certain information from a contributor’s PR, does some basic analysis/calculation on this, and then posts back to the PR thread with a rough score, in a way creating a very rudimentary initial scoring flow.

We see this as a beta example of what the flow could look like for fixed criteria scoring, then evaluation DAO would come in and perform more significant reviewal which would serve to multiply a contributor’s base score further. Of course, all of the values that we used within the script for calculating score can and should be changed (+ votable), though we’ve hardcoded a few values just to provide an example of what this could look like in basic, full-form.

This is not at all to be seen as finalized nor is it a guaranteed idea that we will move forward with; rather it is simply an example of something that we could use to kickstart GoR evaluation. At this point we want to share the work we’ve done so far and gather initial feedback before investing more time further exploring this.

#### Flow:
- User opens up PR with their contribution on one of the GoR-eligible repositories (in the video we are using a private repository on my personal account for testing purposes)
User awaits CI (continuous integration; automation that runs on a repository to serve various purposes)
- In our case, we use CI to run the GoR point calculation script.
    - This will trigger immediately following a PR’s creation, meaning points can be awarded within a few seconds of a user’s submission, thus closing the loop on users getting an initial touchpoint by our team and feeling valued/inspired since they will already have some aspect of their contribution graded (a small amount of token can be sent out here during this step as an act of “good faith” if we wish/if legal allows; I think something would be good to share here, perhaps even an NFT gets minted and dropped to the user’s account denoting their contribution (at the very least, some acknowledgement of their contribution would be good)
- The CI finishes and the user is presented with 2 messages from our team (currently it is my account but this can be changed to a bot account if we wish; ie, GoR-Bot):
    - Message 1: Points awarded
    - Message 2: Reward distribution/receipt/thanks
- The user now awaits a more serious review from Evaluation DAO where they will receive a multiplier on their base points that we’ve just calculated with this initial scoring algorithm
