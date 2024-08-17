Snake game AI based on reinforcemnet learning.
We have agent which is the computer player that interact with the 
environment which is the game where the agent gets reward based on what
it is doing. Positive reward indicate actions that are favourable.

The learning process happen through a neural network.

By controlling this reward we can assist the agent to perform more task
that maximises the reward. However its the job of the agent to figure
out how to find conditions that maximise reward.

SnakeGame 1.0

conda env list
conda activate snake_game

Agent:
- game
- model

For training:
- state = get_state(game)
- action = get_action(state) -> model.predict()
- reward, score, game_over? = game.play_step(action)
- new_state = get_state(game)
- save(new_state)
- model.train()

Rewards:
+10 food
-10 game over 
0 else

Actions:
This action is wrt current direction
[1,0,0] - straight
[0,1,0] - right
[0,0,1] - left

State:
The state of game sanke will be aware of
[danger straight, danger right, danger left,

direction up, direction right,
direction down, direction left,

food left, food right,
food up, food down]
All boolean values

Model:
model takes in the current state of the game from snake and output the
direction in which it should go.
11[state size]*hidden*3[action] neural network

Deep Q learning:
- initial state of the game
- choose an action -> model.predict()
- preform action
- measure reward
- update Q value + train model

Observations:
- Record scroe is not exceeding 70, this may be because when the length is larger it is still in greedy mode
  and going after food irrespective if there is any space left after consuming food.
- Applying flood fill algo to assess beforehand if there is atleast snake's length amount of space is availble
  before moving.
- Record 120 is not breaking when using flood fill algo
- 

TODO:
- save model for ready to use basis
- create multiple models for diff stages
- create mega model that will use mini models for training
- exapnding playfield
- checkpoint training
- improve performance
- create new game with powers and obstacles