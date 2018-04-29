from util.plotly import Plot, multiplot
import numpy as np

p1 = Plot("", "<i>Sin Function</i>", "", font_family="Times", font_size=18)
f1 = lambda x: (np.sin(x) - .3)**2
p1.add_func("<i>Sin Function</i>", f1, [-np.pi, np.pi])
# p1.plot(file_name="test.html", show=False)

p2 = Plot("<i>Sample Functions</i>", "<i>Cosine Function</i>", 
          "y axis", font_family="Times", font_size=18)
f2 = lambda x: (np.cos(x) - .3)**2
p2.add_func("<i>Cosine Function</i>", f2, [-np.pi, np.pi], color=p2.color(1))

multiplot([p1,p2], file_name="test.html", show=False,
          show_legend=False, shared_y=True)
