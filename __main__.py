import regent_ai
import gymnasium as gym

env = gym.make(id='Regent-v0')
observation, info = env.reset()
for _ in range(100):
    action = env.action_space.sample()
    _, reward, terminated, truncated, _ = env.step(action)

    if terminated or truncated:
        observation, _ = env.reset()

env.close()
