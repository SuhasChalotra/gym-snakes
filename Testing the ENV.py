import gym
import gym_snakes
import time
import random
import numpy as np
import tflearn
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
from statistics import mean, median
from collections import Counter

LR = 1e-3
env = gym.make('Snakes-v0')
env.reset()
goal_steps = 500
score_requirement = 50
initial_games = 10000


def some_random_games():
    for episode in range(5):
        env.reset()
        for t in range(goal_steps):
            env.render()
            action = env.action_space.sample()
            observation, reward, done, info = env.step(action)
            if done:
                break


#some_random_games()


def initial_population():
    training_data = []
    scores = []
    accepted_scores = []

    for _ in range(initial_games):
        score = []
        game_memory = []
        prev_observation = []
        for _ in range(goal_steps):
            action = [random.randrange(0, 4)for _ in range(2)]

            observation, reward, done, info = env.step(action)

            if len(prev_observation) > 0:
                game_memory.append([prev_observation, action])

            prev_observation = observation

            score += reward

            if done:
                break

        if score > score_requirement:
            accepted_scores.append(score)
            for data in game_memory:
                if data[1] == 1:
                    output = [0, 1]
                elif data[1] == 0:
                    output = [1, 0]

                training_data.append([data[0], output])

        env.reset()
        scores.append(score)
    training_data_save = np.array(training_data)
    np.save('saved.npy', training_data_save)

    print("Average accepted score:", mean(accepted_scores))
    print("Median score for accepted score", median(accepted_scores))
    print(Counter(accepted_scores))

    return training_data


def neural_network_model(input_size):
    network = input_data(shape=[None, input_size, 1], name='input')

    network = fully_connected(network, 256, activation='relu')
    network = dropout(network, 0.8)

    network = fully_connected(network, 256, activation='relu')
    network = dropout(network, 0.8)

    network = fully_connected(network, 512, activation='relu')
    network = dropout(network, 0.8)

    network = fully_connected(network, 256, activation='relu')
    network = dropout(network, 0.8)

    network = fully_connected(network, 128, activation='relu')
    network = dropout(network, 0.8)

    network = fully_connected(network, 2, activation='softmax')
    network = regression(network, optimizer='adam', learning_rate=LR, loss='categorical_crossentropy', name='targets')

    network_var_model = tflearn.DNN(network, tensorboard_dir='log')

    return network_var_model


def train_model(training_Data, model=False):

    X = np.array([i[0] for i in training_Data]).reshape(-1, len(training_Data[0][0]), 1)
    # what does reshape do?
    y = [i[1] for i in training_Data]

    if not model:
        model = neural_network_model(input_size=len(X[0]))
    model.fit({'input': X}, {'targets': y}, n_epoch=3, snapshot_step=500, show_metric=True, run_id='openAI')
    return model


#training_data = initial_population()
#model = train_model(training_data)


scores = []
choices = []

for each_game in range(10):
    score = []
    game_memory = []
    prev_obv = []
    env.reset()

    for _ in range(goal_steps):
        env.render()
        time.sleep(.1)

        if len(prev_obv) == 0:
            action = [random.randrange(0, 4) for _ in range(2)]
        #else:
         #   action = np.argmax(model.predict(prev_obv.reshape(-1, len(prev_obv), 1))[0])

        choices.append(action)

        new_observation, reward, done, info = env.step(action)
        prev_obv = new_observation
        game_memory.append([new_observation, action])
        score.append(reward)
        if done:
            break

    scores.append(score)

#model.save('new.model')
#print("Average Score", sum(scores)/len(scores))
#print("Choice 1: {}, Choice 2: {}".format(choices.count(1)/len(choices), choices.count(0)/len(choices)))
