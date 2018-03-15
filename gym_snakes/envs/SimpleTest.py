import gym
import gym_snakes
import time

env = gym.make('Snakes-v0')

for i in range(10):
    env.reset()
    for t in range(1000):
        env.render()
        time.sleep(.05)
        observation, reward, done, info = env.step(env.action_space.sample())
        if done:
            print('episode {} finished after {} timesteps'.format(i, t))
            break