import hopper_controller

env = gym.make("Hopper-v5")
obs = env.reset()
while True:
    action = hopper_controller.act(obs)
    obs, reward, done, _ = env.step(action)
    if done:
        break
