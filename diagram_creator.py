import numpy as np  
import matplotlib.pyplot as plt
import matplotlib.hatch
from matplotlib.hatch import HatchPatternBase
from matplotlib.path import Path

#climate data for Addis-Ababa
#x = np.array(["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"])
x = np.arange(0.5, 12.5, 1)
x_nolabel = 12 * " "

T_mean = np.array([15.9, 16.4, 17.9, 17.8, 17.6, 16.6, 15.0, 15.0, 15.6, 15.8, 15.6, 15.2])
#T_mean = np.array([-15.9, 16.4, 17.9, 17.8, 17.6, 16.6, 15.0, 15.0, 15.6, 15.8, 15.6, 15.2]) #test data

m_daily_mean = np.array([6.1, 8.3, 9.4, 10.0, 10.0, 9.4, 10.0, 10.0, 9.4, 7.2, 6.1, 5.0])
#m_daily_mean = np.array([-6.1, 8.3, 9.4, -10.0, 10.0, 9.4, 10.0, 10.0, -9.4, 7.2, 6.1, 5.0]) #test data

P = np.array([14, 37, 70, 85, 90, 134, 285, 295, 196, 21, 13, 6]) #JAN, FEB, OCT, NOV, DEC drought

##creating Walter--Lieth y-axis scalings
#dynamic Temp-y label
T_sorted = np.sort(T_mean)
if -10 <= T_sorted[0] < 0:
    T_ticks  = [-10, 0, 10, 20, 30, 40, 50, 60]
    T_labels = ["-10", "0", "10", "20", "30", "40", "50", ""]
    y_min = -10
elif -20 <= T_sorted[0] < -10:
    T_ticks  = [-20, -10, 0, 10, 20, 30, 40, 50, 60]
    T_labels = ["-20", "-10", "0", "10", "20", "30", "40", "50", ""]
    y_min = -20
else:
    T_ticks  = [0, 10, 20, 30, 40, 50, 60]
    T_labels = ["0", "10", "20", "30", "40", "50", ""]
    y_min = 0

#tricky part: the latent scaling
P_latent_labels = ["0", "20", "40", "60", "80", "100", "300"]

def create_P_latent(P):
    P_latent = []
    for p in P:
        if p <= 100:
            P_latent.append(p)
        elif 100 < p < 300:
            P_latent.append(100 + (p-100)/10)
        else:
            print("P should be less than 300 mm")
            return None
    return P_latent
P_latent = np.array(create_P_latent(P))

#defining _ hatch
class CustomHatch(HatchPatternBase):
    def __init__(self, hatch, density):
        self.num_lines = int(hatch.count('_') * density) #num of lines based on how many hatches provided
        self.num_vertices = (self.num_lines ** 2) * 2 #num of rows and columns -> num_lines**2 = num of hatches on the tile; *2 -> num of vertices
        
    def set_vertices_and_codes(self, vertices, codes):
        steps = np.linspace(0.0, 1.0, self.num_lines, endpoint=False)
        
        idx = 0
        for y in steps: #iterate on grid points
            for x in steps: #dash starts at 0.2, ends at 0.8; in the center of the cell
                vertices[idx] = [x + 0.2 / self.num_lines, y + 0.5 / self.num_lines] #dash startpoint
                vertices[idx+1] = [x + 0.8 / self.num_lines, y + 0.5 / self.num_lines] #dash endpoint
                
                codes[idx] = Path.MOVETO
                codes[idx+1] = Path.LINETO
                idx += 2 #bc every dash has 2 indices

#registering hatch
if CustomHatch not in matplotlib.hatch._hatch_types:
    matplotlib.hatch._hatch_types.append(CustomHatch)

##plotting
fig, ax1 = plt.subplots()
ax1.plot(x, T_mean, "r-o")
ax1.set_xticks(range(len(x)))
ax1.set_xticklabels(x_nolabel)
ax1.set_yticks(T_ticks)
ax1.set_yticklabels(T_labels)
ax1.set_ylim(y_min, 60)
ax1.set_xlim(left=0)

ax2 = ax1.twinx()
ax2.plot(x, create_P_latent(P), "b-o")
ax2.set_yticks([0, 20, 40, 60, 80, 100, 120])
ax2.set_yticklabels(P_latent_labels)
if y_min == -20:
    ax2.set_ylim(-40, 120)
elif y_min == -10:
    ax2.set_ylim(-20, 120)
else:
    ax2.set_ylim(0, 120)

plt.hlines(y=0, xmin=0, xmax=12.5, colors="black", lw=1.5)
fig.tight_layout()
ax1.grid(True)

#labeling
ax1.text(0, 1.002, "Addisz-Abeba\n2355", transform=ax1.transAxes, ha="left", va="bottom", fontsize=15)
ax1.text(-0.05, 0.8, "34,4\n25,0", transform=ax1.transAxes, ha="left", va="bottom", fontsize=15)
ax1.text(-0.05, -0.01, "10,0\n0,0", transform=ax1.transAxes, ha="left", va="bottom", fontsize=15)
ax2.text(1, 1.002, "16,2\n1246", transform=ax2.transAxes, ha="right", va="bottom", fontsize=15)

#aridity
ax2.fill_between(x, P_latent, 100, where=(P_latent > 100), interpolate=True, alpha=0.9, color="navy") #superhumid
ax2.fill_between(x, P_latent, T_mean * 2, where=(P_latent > T_mean * 2), interpolate=True, facecolor="none", hatch="|", edgecolor="navy") #humid
ax2.fill_between(x, P_latent, T_mean * 2, where=(P_latent < T_mean * 2), interpolate=True, facecolor="none", hatch=".", edgecolor="navy") #arid 
ax2.fill_between(x, P_latent / 3, P_latent, where=(P_latent / 3 < T_mean), interpolate=True, facecolor="none", hatch="_", edgecolor="navy") #drought

#frosty months
for i in range(12):
    if m_daily_mean[i] < 0:
        plt.hlines(y=0, xmin=i, xmax=i + 1, colors="black", lw=8)


plt.show()
