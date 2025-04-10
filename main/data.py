import matplotlib.pyplot as plt

# Your recorded data
sample_sizes = [500, 1000, 2000, 4000, 8000]
win_percentages = [58.6, 55.6, 60.1, 60.675, 59.1625]
avg_turns = [15.086, 15.303, 14.839, 14.85025, 14.92575]
variance_turns = [18.5036, 18.7239, 18.7545, 18.3434, 18.7988]

# Create the figure
plt.figure(figsize=(14, 6))

# Win Percentage plot
plt.subplot(1, 3, 1)
plt.plot(sample_sizes, win_percentages, marker='o', color='green')
plt.title("Win Percentage vs Sample Size")
plt.xlabel("Sample Size")
plt.ylabel("Win %")
plt.grid(True)

# Average Turns plot
plt.subplot(1, 3, 2)
plt.plot(sample_sizes, avg_turns, marker='o', color='blue')
plt.title("Average Turns vs Sample Size")
plt.xlabel("Sample Size")
plt.ylabel("Average Turns")
plt.grid(True)

# Turn Variance plot
plt.subplot(1, 3, 3)
plt.plot(sample_sizes, variance_turns, marker='o', color='red')
plt.title("Turn Variance vs Sample Size")
plt.xlabel("Sample Size")
plt.ylabel("Variance")
plt.grid(True)

plt.tight_layout()
plt.savefig("ai_convergence_plot.png")
plt.show()
