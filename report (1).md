# Reprot for assignment 2 - Tom Shur 327615787
## Task 1
Created an elipse:
```py elipse
# elipse:
num_points = 100
theta = np.linspace(0, 2 * np.pi, num_points, endpoint=False) # 0<=theta<=2pi
radius_x, radius_y = 1.0, 0.3
vertices = np.column_stack((radius_x * np.cos(theta), radius_y * np.sin(theta))) # this is the geometric place of the points of the elipse, here we sample 100 points from it
segments = np.column_stack((np.arange(num_points), np.roll(np.arange(num_points), -1))) # segments connecting consecutive points to form the boundary
input_data = {"vertices": vertices, "segments": segments}
tris = tr.triangulate(input_data, 'p')  # 'p' preserves the input boundary

V = tris['vertices']
F = tris['triangles']
```
![image](https://github.com/user-attachments/assets/93e48499-22ea-4f5a-b29b-428ab00ad3d4)

Notice the "intersection" points in the triangulation are on the boundry of the shape, so there are no intirior points.
## Task 2:
1. I wrote a function print_to_window that prints given text to window, and optionally removes the last written text. This is done using a global variable window_text.
   ```py print_to_window
   window_text = vd.Text2D("", pos="top-left", c="green", font="Arial")

   def print_to_window(new_text, remove=False):
    global window_text
    old_text = ""
    if not remove:
        old_text = window_text.text() + "\n"
    plt.remove(window_text)
    window_text = vd.Text2D(old_text + new_text, pos="top-left", c="green", font="Arial")
    plt.add(window_text)


   def OnLeftButtonPress(event):
    global window_text

    if event.object is None:          # mouse hits nothing, return.
        print('Mouse hits nothing')
    if isinstance(event.object,vd.mesh.Mesh):          # mouse hits the mesh
        Vi = vdmesh.closest_point(event.picked3d, return_point_id=True)
        # print('Mouse hits the mesh')
        # print('Coordinates:', event.picked3d)
        # print('Point ID:', Vi)
        print_to_window('Mouse hits the mesh', remove=True)
        print_to_window('Coordinates:' + str(event.picked3d))
        print_to_window('Point ID:' + str(Vi))
        if Vi not in pinned_vertices:
            pinned_vertices.append(Vi)
        else:
            pinned_vertices.remove(Vi)
    redraw()

   ```
   

https://github.com/user-attachments/assets/32acaae0-4b8e-4436-bd4d-de20f65bc881

2. While the 'F' key is pressed, the pinned vertices follow the movment of the mouse cursor.
   To identify when the 'F' key is being pressed, a global variable is_f_pressed is maintained through callbacks to OnKeyboardPress and OnKeyboardRelease.
   Using the angle and speed of the mouse, we calculate the diffrance in movement that will be added to the pinned vertices (notice that the movement also factors in the speed of the mouse to make it more similiar to the mouse movement and          allow fast changes).
   ```py pinned vertices follow mouse 
   
      is_f_pressed = False # global variable to track if the 'f' key is pressed
      
      def OnKeyboardPress(event):
          global is_f_pressed
      
          if event.keypress in ['f', 'F']:
              is_f_pressed = True 
      
      
      def OnKeyboardRelease(event):
          global is_f_pressed
      
          if event.keypress in ['f', 'F']:
              is_f_pressed = False 
      
      
      def OnMouseMove(event):
          global is_f_pressed, pinned_vertices, V
      
          if is_f_pressed and len(pinned_vertices) > 0:  # if 'f' is pressed and there are pinned vertices
              if event.delta2d[0] != 0 or event.delta2d[1] != 0:  # if the mouse is moving
                  mouse_angle = event.angle2d
                  mouse_pos_change_normalized = np.array([np.cos(mouse_angle), np.sin(mouse_angle)])
      
                  mouse_speed = event.speed2d * 0.01 # 0.01 is a constant for scaling
                  V[pinned_vertices, 0] += mouse_pos_change_normalized[0] * mouse_speed
                  V[pinned_vertices, 1] += mouse_pos_change_normalized[1] * mouse_speed
                  redraw()

   ```

   

https://github.com/user-attachments/assets/66927cf8-a2da-4c5b-a1b5-d680d504e95a

3. Changed the code so that vertices have a third coordinate now, initialized to 0:
   ```py Z coordinate added
   # V = tris['vertices']
   V = np.column_stack((tris['vertices'], np.zeros(tris['vertices'].shape[0]))) # add z coordinate to the vertices
   ```
   While the user is pressing 'Z' key, the third coordiante is changed according to the vertical movement of the mouse cursor. Also, whenever 'R' button is clicked, the z coordinate of all points is set to 0 ("going back to 2d").
   ```py
      
      is_f_pressed = False # global variable to track if the 'f' key is pressed
      is_z_pressed = False # global variable to track if the 'z' key is pressed
      
      def OnKeyboardPress(event):
          global is_f_pressed, is_z_pressed
      
          if event.keypress in ['f', 'F']:
              is_f_pressed = True 
          if event.keypress in ['z', 'Z']:
              is_z_pressed = True 
          if event.keypress in ['r', 'R']:
              V[:,2] = 0.0
              redraw()
      
      
      def OnKeyboardRelease(event):
          global is_f_pressed, is_z_pressed
      
          if event.keypress in ['f', 'F']:
              is_f_pressed = False 
          if event.keypress in ['z', 'Z']:
              is_z_pressed = False 
      
      
      def OnMouseMove(event):
          global is_f_pressed, is_z_pressed, pinned_vertices, V
      
          if is_f_pressed and len(pinned_vertices) > 0:  # if 'f' is pressed and there are pinned vertices
              if event.delta2d[0] != 0 or event.delta2d[1] != 0:  # if the mouse is moving
                  mouse_angle = event.angle2d
                  mouse_pos_change_normalized = np.array([np.cos(mouse_angle), np.sin(mouse_angle)])
      
                  mouse_speed = event.speed2d * 0.01 # 0.01 is a constant for scaling
                  V[pinned_vertices, 0] += mouse_pos_change_normalized[0] * mouse_speed
                  V[pinned_vertices, 1] += mouse_pos_change_normalized[1] * mouse_speed
                  redraw()
          if is_z_pressed and len(pinned_vertices) > 0:  # if 'z' is pressed and there are pinned vertices
              if event.delta2d[0] != 0 or event.delta2d[1] != 0:  # if the mouse is moving
                  mouse_angle = event.angle2d
                  mouse_pos_change_normalized = np.sin(mouse_angle)
                  V[pinned_vertices, 2] += mouse_pos_change_normalized * 0.01
      
                  redraw()
    
   ```
   




https://github.com/user-attachments/assets/5987124f-6abb-4302-af15-ea3dfdb83919


## Task 3:
1. First I did a minor change in the method ```BacktrackingLineSearch``` in the class ```MeshOptimizer```: added the line ```d = d.reshape(x0.shape)``` so that the direction vector ```d``` and the given initial mesh configuration ```x0``` would be of the same shape (since we pass ```V``` not flatten but ```d``` is by default a one dimensional vector of the DOFs.
```py
def BacktrackingLineSearch(self, x, d, alpha=1, max_iter=100):
        """
        Perform backtracking line search to find a step size that reduces the energy.
        
        Args:
            x: Current mesh configuration
            d: Search direction
            alpha: Initial step size
            max_iter: Maximum number of backtracking steps
        Returns:
            Tuple of (new configuration, step size)
        """
        x0 = x.copy()
        f0 = self.femMesh.compute_energy(x0)


        d = d.reshape(x0.shape)  # ensure d is the same shape as x0



        for _ in range(max_iter):
            if self.femMesh.compute_energy(x0 + alpha*d) <= f0:
                return x0 + alpha*d, alpha
            alpha *= 0.5
        return x0, alpha  # Return original point if no improvement found
```
To run and show the optimization in each step, I initialized the mesh, the optimizer and x in the main and plotted the mesh:
```py
femMesh = FEMMesh(V, F, ZeroLengthSpringEnergy(dim=3), EdgeStencil(dim=3)) # create the mesh object
optimizer = MeshOptimizer(femMesh) # create the optimizer object
x = V.copy() # initialize x to the original shape

vdmesh = vd.Mesh([x,F]).linecolor('black')
plt += vdmesh
plt += vd.Points(x[pinned_vertices,:])
plt.user_mode('2d').show().close()
```

Changed OnKeyboardPress function so that every time 'O' key is pressed, a step of the optimization is done:
```py
if event.keypress in ['o', 'O']:
        # x = optimizer.optimize(x, max_iter=1) # optimize the mesh configuration
        # x = x.reshape(V.shape) # reshape x to the original shape

        try:
            V = optimizer.optimize(V, max_iter=1) # optimize the mesh configuration
        except Exception as e: print(f'error: {e}')

        V = V.reshape(V_initial.shape) # reshape x to the original shape
        redraw()
```

I implemented the finite diffrances gradient and hessian in ElementEnergy class:
```py
def gradient_fd(self, *args):
        # TODO
        
        X1, X2, x1, x2 = args

        h=0.0000001
        grad = np.zeros(2*self.dim)


        if self.dim==2:
            func = lambda x1_, y1_, x2_, y2_: self.energy(X1, X2, np.array([x1_, y1_]), np.array([x2_, y2_]))
            
            x1_, y1_ = x1[0], x1[1]
            x2_, y2_ = x2[0], x2[1]

            gx1 = (func(x1_+h, y1_, x2_, y2_) - func(x1_-h, y1_, x2_, y2_)) / (2*h)
            gy1 = (func(x1_, y1_+h, x2_, y2_) - func(x1_, y1_-h, x2_, y2_)) / (2*h)
            gx2 = (func(x1_, y1_, x2_+h, y2_) - func(x1_, y1_, x2_-h, y2_)) / (2*h)
            gy2 = (func(x1_, y1_, x2_, y2_+h) - func(x1_, y1_, x2_, y2_-h)) / (2*h)

            grad[:self.dim] = np.array([gx1, gy1])
            grad[self.dim:] = np.array([gx2, gy2])
        else: # dim == 3
            func = lambda x1_, y1_, z1_, x2_, y2_, z2_: self.energy(X1, X2, np.array([x1_, y1_, z1_]), np.array([x2_, y2_, z2_]))
            
            x1_, y1_, z1_ = x1[0], x1[1], x1[2]
            x2_, y2_, z2_ = x2[0], x2[1], x2[2]
            gx1 = (func(x1_+h, y1_, z1_, x2_, y2_, z2_) - func(x1_-h, y1_, z1_, x2_, y2_, z2_)) / (2*h)
            gy1 = (func(x1_, y1_+h, z1_, x2_, y2_, z2_) - func(x1_, y1_-h, z1_, x2_, y2_, z2_)) / (2*h)
            gz1 = (func(x1_, y1_, z1_+h, x2_, y2_, z2_) - func(x1_, y1_, z1_-h, x2_, y2_, z2_)) / (2*h)
            gx2 = (func(x1_, y1_, z1_, x2_+h, y2_, z2_) - func(x1_, y1_, z1_, x2_-h, y2_, z2_)) / (2*h)
            gy2 = (func(x1_, y1_, z1_, x2_, y2_+h, z2_) - func(x1_, y1_, z1_, x2_, y2_-h, z2_)) / (2*h)
            gz2 = (func(x1_, y1_, z1_, x2_, y2_, z2_+h) - func(x1_, y1_, z1_, x2_, y2_, z2_-h)) / (2*h)

            grad[:self.dim] = np.array([gx1, gy1, gz1])
            grad[self.dim:] = np.array([gx2, gy2, gz2])
        return grad

    def hessian_fd(self, *args):
        # TODO

        X1, X2, x1, x2 = args

        h=0.001
        hassian = np.zeros((2*self.dim, 2*self.dim))

        if self.dim==2:
            func = lambda x1_, y1_, x2_, y2_: self.energy(X1, X2, np.array([x1_, y1_]), np.array([x2_, y2_]))

            x1_, y1_ = x1[0], x1[1]
            x2_, y2_ = x2[0], x2[1]

            gx1x1 = (func(x1_+h, y1_, x2_, y2_) - 2*func(x1_, y1_, x2_, y2_) + func(x1_-h, y1_, x2_, y2_)) / h**2
            gy1y1 = (func(x1_, y1_+h, x2_, y2_) - 2*func(x1_, y1_, x2_, y2_) + func(x1_, y1_-h, x2_, y2_)) / h**2
            gx2x2 = (func(x1_, y1_, x2_+h, y2_) - 2*func(x1_, y1_, x2_, y2_) + func(x1_, y1_, x2_-h, y2_)) / h**2
            gy2y2 = (func(x1_, y1_, x2_, y2_+h) - 2*func(x1_, y1_, x2_, y2_) + func(x1_, y1_, x2_, y2_-h)) / h**2
            gx1y1 = (func(x1_+h, y1_+h, x2_, y2_) - func(x1_+h, y1_-h, x2_, y2_) - func(x1_-h, y1_+h, x2_, y2_) + func(x1_-h, y1_-h, x2_, y2_)) / (4*h**2)
            gx1x2 = (func(x1_+h, y1_, x2_+h, y2_) - func(x1_+h, y1_, x2_-h, y2_) - func(x1_-h, y1_, x2_+h, y2_) + func(x1_-h, y1_, x2_-h, y2_)) / (4*h**2)
            gx1y2 = (func(x1_+h, y1_, x2_, y2_+h) - func(x1_+h, y1_, x2_, y2_-h) - func(x1_-h, y1_, x2_, y2_+h) + func(x1_-h, y1_, x2_, y2_-h)) / (4*h**2)
            gy1x2 = (func(x1_, y1_+h, x2_+h, y2_) - func(x1_, y1_+h, x2_-h, y2_) - func(x1_, y1_-h, x2_+h, y2_) + func(x1_, y1_-h, x2_-h, y2_)) / (4*h**2)
            gy1y2 = (func(x1_, y1_+h, x2_, y2_+h) - func(x1_, y1_+h, x2_, y2_-h) - func(x1_, y1_-h, x2_, y2_+h) + func(x1_, y1_-h, x2_, y2_-h)) / (4*h**2)
            gx2y2 = (func(x1_, y1_, x2_+h, y2_+h) - func(x1_, y1_, x2_+h, y2_-h) - func(x1_, y1_, x2_-h, y2_+h) + func(x1_, y1_, x2_-h, y2_-h)) / (4*h**2)




            hassian[:self.dim, :self.dim] = np.array([[gx1x1, gx1y1], [gx1y1, gy1y1]])
            hassian[self.dim:, self.dim:] = np.array([[gx2x2, gx2y2], [gx2y2, gy2y2]])
            hassian[:self.dim, self.dim:] = np.array([[gx1x2, gx1y2], [gy1x2, gy1y2]])
            hassian[self.dim:, :self.dim] = np.array([[gx1x2, gy1x2], [gx1y2, gy1y2]])

        else: # dim == 3
            # TODO
            
            func = lambda x1_, y1_, z1_, x2_, y2_, z2_: self.energy(X1, X2, np.array([x1_, y1_, z1_]), np.array([x2_, y2_, z2_]))
            
            x1_, y1_, z1_ = x1[0], x1[1], x1[2]
            x2_, y2_, z2_ = x2[0], x2[1], x2[2]
            gx1x1 = (func(x1_+h, y1_, z1_, x2_, y2_, z2_) - 2*func(x1_, y1_, z1_, x2_, y2_, z2_) + func(x1_-h, y1_, z1_, x2_, y2_, z2_)) / h**2
            gy1y1 = (func(x1_, y1_+h, z1_, x2_, y2_, z2_) - 2*func(x1_, y1_, z1_, x2_, y2_, z2_) + func(x1_, y1_-h, z1_, x2_, y2_, z2_)) / h**2
            gz1z1 = (func(x1_, y1_, z1_+h, x2_, y2_, z2_) - 2*func(x1_, y1_, z1_, x2_, y2_, z2_) + func(x1_, y1_, z1_-h, x2_, y2_, z2_)) / h**2
            gx2x2 = (func(x1_, y1_, z1_, x2_+h, y2_, z2_) - 2*func(x1_, y1_, z1_, x2_, y2_, z2_) + func(x1_, y1_, z1_, x2_-h, y2_, z2_)) / h**2
            gy2y2 = (func(x1_, y1_, z1_, x2_, y2_+h, z2_) - 2*func(x1_, y1_, z1_, x2_, y2_, z2_) + func(x1_, y1_, z1_, x2_, y2_-h, z2_)) / h**2
            gz2z2 = (func(x1_, y1_, z1_, x2_, y2_, z2_+h) - 2*func(x1_, y1_, z1_, x2_, y2_, z2_) + func(x1_, y1_, z1_, x2_, y2_, z2_-h)) / h**2
            # f
            gx1y1 = (func(x1_+h, y1_+h, z1_, x2_, y2_, z2_) - func(x1_+h, y1_-h, z1_, x2_, y2_, z2_) - func(x1_-h, y1_+h, z1_, x2_, y2_, z2_) + func(x1_-h, y1_-h, z1_, x2_, y2_, z2_)) / (4*h**2)
            gx1z1 = (func(x1_+h, y1_, z1_+h, x2_, y2_, z2_) - func(x1_+h, y1_, z1_-h, x2_, y2_, z2_) - func(x1_-h, y1_, z1_+h, x2_, y2_, z2_) + func(x1_-h, y1_, z1_-h, x2_, y2_, z2_)) / (4*h**2)
            gx1x2 = (func(x1_+h, y1_, z1_, x2_+h, y2_, z2_) - func(x1_+h, y1_, z1_, x2_-h, y2_, z2_) - func(x1_-h, y1_, z1_, x2_+h, y2_, z2_) + func(x1_-h, y1_, z1_, x2_-h, y2_, z2_)) / (4*h**2)
            gx1y2 = (func(x1_+h, y1_, z1_, x2_, y2_+h, z2_) - func(x1_+h, y1_, z1_, x2_, y2_-h, z2_) - func(x1_-h, y1_, z1_, x2_, y2_+h, z2_) + func(x1_-h, y1_, z1_, x2_, y2_-h, z2_)) / (4*h**2)
            gx1z2 = (func(x1_+h, y1_, z1_, x2_, y2_, z2_+h) - func(x1_+h, y1_, z1_, x2_, y2_, z2_-h) - func(x1_-h, y1_, z1_, x2_, y2_, z2_+h) + func(x1_-h, y1_, z1_, x2_, y2_, z2_-h)) / (4*h**2)
            #
            gy1z1 = (func(x1_, y1_+h, z1_+h, x2_, y2_, z2_) - func(x1_, y1_+h, z1_-h, x2_, y2_, z2_) - func(x1_, y1_-h, z1_+h, x2_, y2_, z2_) + func(x1_, y1_-h, z1_-h, x2_, y2_, z2_)) / (4*h**2)
            gy1x2 = (func(x1_, y1_+h, z1_, x2_+h, y2_, z2_) - func(x1_, y1_+h, z1_, x2_-h, y2_, z2_) - func(x1_, y1_-h, z1_, x2_+h, y2_, z2_) + func(x1_, y1_-h, z1_, x2_-h, y2_, z2_)) / (4*h**2)
            gy1y2 = (func(x1_, y1_+h, z1_, x2_, y2_+h, z2_) - func(x1_, y1_+h, z1_, x2_, y2_-h, z2_) - func(x1_, y1_-h, z1_, x2_, y2_+h, z2_) + func(x1_, y1_-h, z1_, x2_, y2_-h, z2_)) / (4*h**2)
            gy1z2 = (func(x1_, y1_+h, z1_, x2_, y2_, z2_+h) - func(x1_, y1_+h, z1_, x2_, y2_, z2_-h) - func(x1_, y1_-h, z1_, x2_, y2_, z2_+h) + func(x1_, y1_-h, z1_, x2_, y2_, z2_-h)) / (4*h**2)
            #
            gz1x2 = (func(x1_, y1_, z1_+h, x2_+h, y2_, z2_) - func(x1_, y1_, z1_+h, x2_-h, y2_, z2_) - func(x1_, y1_, z1_-h, x2_+h, y2_, z2_) + func(x1_, y1_, z1_-h, x2_-h, y2_, z2_)) / (4*h**2)
            gz1y2 = (func(x1_, y1_, z1_+h, x2_, y2_+h, z2_) - func(x1_, y1_, z1_+h, x2_, y2_-h, z2_) - func(x1_, y1_, z1_-h, x2_, y2_+h, z2_) + func(x1_, y1_, z1_-h, x2_, y2_-h, z2_)) / (4*h**2)
            gz1z2 = (func(x1_, y1_, z1_+h, x2_, y2_, z2_+h) - func(x1_, y1_, z1_+h, x2_, y2_, z2_-h) - func(x1_, y1_, z1_-h, x2_, y2_, z2_+h) + func(x1_, y1_, z1_-h, x2_, y2_, z2_-h)) / (4*h**2)
            #
            gx2y2 = (func(x1_, y1_, z1_, x2_+h, y2_+h, z2_) - func(x1_, y1_, z1_, x2_+h, y2_-h, z2_) - func(x1_, y1_, z1_, x2_-h, y2_+h, z2_) + func(x1_, y1_, z1_, x2_-h, y2_-h, z2_)) / (4*h**2)
            gx2z2 = (func(x1_, y1_, z1_, x2_+h, y2_, z2_+h) - func(x1_, y1_, z1_, x2_+h, y2_, z2_-h) - func(x1_, y1_, z1_, x2_-h, y2_, z2_+h) + func(x1_, y1_, z1_, x2_-h, y2_, z2_-h)) / (4*h**2)
            #
            gy2z2 = (func(x1_, y1_, z1_, x2_, y2_+h, z2_+h) - func(x1_, y1_, z1_, x2_, y2_+h, z2_-h) - func(x1_, y1_, z1_, x2_, y2_-h, z2_+h) + func(x1_, y1_, z1_, x2_, y2_-h, z2_-h)) / (4*h**2)


            hassian[:self.dim, :self.dim] = np.array([[gx1x1, gx1y1, gx1z1], [gx1y1, gy1y1, gy1z1], [gx1z1, gy1z1, gz1z1]]) #
            hassian[self.dim:, self.dim:] = np.array([[gx2x2, gx2y2, gx2z2], [gx2y2, gy2y2, gy2z2], [gx2z2, gy2z2, gz2z2]]) #
            hassian[:self.dim, self.dim:] = np.array([[gx1x2, gx1y2, gx1z2], [gy1x2, gy1y2, gy1z2], [gz1x2, gz1y2, gz1z2]]) #
            hassian[self.dim:, :self.dim] = np.array([[gx1x2, gy1x2, gz1x2], [gx1y2, gy1y2, gz1y2], [gx1z2, gy1z2, gz1z2]]) #
        return hassian
```



And in redraw I changed the code so it would do (at most) one optimization step (so whenever mouse is clicked, we see the updated mesh after one configuration).
```py
def redraw():
    global x
    plt.remove("Mesh")
    # mesh = vd.Mesh([V,F]).linecolor('black')
    x = optimizer.optimize(x, max_iter=1) # optimize the mesh configuration
    x = x.reshape(V.shape) # reshape x to the original shape
    # V = x.copy()

    mesh = vd.Mesh([x,F]).linecolor('black')
    plt.add(mesh)
    plt.remove("Points")
    plt.add(vd.Points(V[pinned_vertices,:],r=10))
    plt.render()
```
I expect to see the mesh getting smaller/more compressed, and eventually probably squashed into one single point, as with ZeroLengthSpringEnergy we assume the rest position of the springs are of length 0, so the optimization will try to minimize the energy of the mesh untill it reaches 0 and the length of the edges is 0.
I also expect that with Newton's method the optimization will be faster than with gradient descent, as Newton's method calculates a quadradic approximation to the function rather than gradient descent that only uses the gradient.

[//]: <> (videos of GD and newton in action)

   
gradient descent:

https://github.com/user-attachments/assets/6083f3cc-72c0-4e93-943f-b784935c7f53

Newton's method:


https://github.com/user-attachments/assets/c30adccf-3a12-4b41-9113-348e3f7d76df



We can see that indeed the mesh's edges always converge to length 0.
Also we can see that grdient descent is mush more gradual than Newton's method (with Newton's method the mesh's energy and the edge lengths are 0 after one iteration).

2. In SpringEnergy class, I added a field ```self.rest_pos_const``` initialized to 0.7 for now, and in the method ```energy``` I initialized the ```rest_length``` to ```rest_length = np.linalg.norm(X1 - X2) * self.rest_pos_const```.

GD:

https://github.com/user-attachments/assets/6d64c16b-a1e4-4592-8ed3-a1149272657e

Newton:

https://github.com/user-attachments/assets/8409a665-5438-401f-8a06-8616249419cf

3. I wrote a class responsible for the added energy (the soft constraint):
   ```py
   class AddedRegularizationEnergy(ElementEnergy):
    def __init__(self, dim=2):
        super().__init__(dim)
        global pinned_vertices, V

        self.lamda = 10
    
    def energy(self, X1, x1):
        return self.lamda * np.linalg.norm(X1 - x1)**2
    def gradient(self, X1, x1):

        grad = np.zeros(self.dim)

        for i in range(self.dim):
            grad[i] = 2*(x1[i] - X1[i]) * self.lamda
        
        return grad
    
    def hessian(self, x1):
        return 2  * self.lamda * np.eye(self.dim)
    
    def set_lamda(self, new_lamda):
        self.lamda = new_lamda
   ```

   Updated the functions in FEMMesh accordingly:


    ```py
    def compute_energy(self,x):
        global pinned_vertices, V

        energy = 0
        for element in self.elements:
            Xi = self.X[element,:]
            xi = x[element,:]
            X_vars = self.stencil.to_variables(Xi)
            x_vars = self.stencil.to_variables(xi)


            energy += self.energy.energy(*X_vars, *x_vars)
        

        for i, vertex in enumerate(self.X):
            if i in pinned_vertices:
                energy += self.added_reg_energy.energy(target_vertices[i], x[i])
        

        return energy

    def compute_gradient(self,x):
        global pinned_vertices, V, target_vertices

        gi = self.compute_local_gradients(x)
        grad = self.assemble_global_gradient(gi)


        # grad_before = grad.copy()

        # for i, vertex in enumerate(self.X):
        for i in range(len(self.X)):
            if i in pinned_vertices:
                # grad[i * self.dim:(i + 1) * self.dim] += self.added_reg_energy.gradient(vertex, x[i])
                grad[i * self.dim:(i + 1) * self.dim] += self.added_reg_energy.gradient(target_vertices[i], x[i])

        return grad


    def compute_hessian(self,x):
        hi = self.compute_local_hessians(x)
        H =  self.assemble_global_hessian(hi)

        for i, vertex in enumerate(self.X):
            if i in pinned_vertices:
                # H[i * self.dim:(i + 1) * self.dim, i * self.dim:(i + 1) * self.dim] += self.added_reg_energy.hessian(x[i])

                # add the hessian of the regularization energy to the hessian matrix, but knowing it is a coo matrix

                H_lil = H.tolil()
                H_lil[i * self.dim:(i + 1) * self.dim, i * self.dim:(i + 1) * self.dim] += self.added_reg_energy.hessian(x[i])
                H = H_lil.tocoo()
 

        
        return H
    ```

    The user can increase/ decrease the value of lamda, the weight for the added energy, by pressing 'W'/'S' keys. So I added the following code to the function OnKeyboardPress:
   ```py
   if event.keypress in ['w', 'W']:
        optimizer.set_lamda(optimizer.femMesh.added_reg_energy.lamda+1)
        print_to_window(f'current lamda : {optimizer.femMesh.added_reg_energy.lamda}')
        redraw()
    if event.keypress in ['s', 'S']:
        if optimizer.femMesh.added_reg_energy.lamda > 0:
            optimizer.set_lamda(optimizer.femMesh.added_reg_energy.lamda-1)
        
        print_to_window(f'current lamda : {optimizer.femMesh.added_reg_energy.lamda}')
        redraw()
   ```
   In each class I added a function to set the value for lamda:

   AddedRegularizationEnergy:
   ```py
   def set_lamda(self, new_lamda):
        self.lamda = new_lamda
   ```

   FEMMesh:
   ```py
   def set_lamda(self, new_lamda):
        self.added_reg_energy.set_lamda(new_lamda)
   ```


   MeshOptimizer:
   ```py
   def set_lamda(self, new_lamda):
        print_to_window("in optimizer set_lamda")
        self.femMesh.set_lamda(new_lamda)
   ```

   for lamda=1:
   

https://github.com/user-attachments/assets/323dc0d3-b8a9-412a-beca-37b330ee185f



   for lamda=10:

   

https://github.com/user-attachments/assets/b44c39f9-e7ab-49a6-9852-3bfd5c594296


   for lamda=100:

   

https://github.com/user-attachments/assets/1d00dda9-96b9-445e-b1a8-a6a1b638d51e


We can see that for higher lamda the movement of the pinned vertices is more limited as a higher weight is given to the constraint. The soft constraints are not equality constraints, so it is not totally guaranteed that the pinned vertices will not move completely' It only punishes vertices that get far from their marked pinned place' so we can see that some of the vertices sometimes swing between two values, probably because the optimization does not completely converge to a final value.

4. .

   ```py
       def gradient(self, X1, X2, x1, x2): # analitycal gradient

        grad = np.zeros(2*self.dim)
        rest_length = np.linalg.norm(X1 - X2) * self.rest_pos_const
        
        grad[:self.dim] = (np.linalg.norm(x1-x2) - rest_length) * (x1 - x2) / np.linalg.norm(x1-x2)
        grad[self.dim:] = (np.linalg.norm(x2-x1) - rest_length) * (x2 - x1) / np.linalg.norm(x2-x1)

        return grad
    


    
    def hessian(self, X1, X2, x1, x2): # analitycal hassian # NOT SURE
        hessian = np.zeros((2*self.dim, 2*self.dim))
        rest_length = np.linalg.norm(X1 - X2) * self.rest_pos_const
        norm_x1x2 = np.linalg.norm(x1-x2)
        
        hessian[:self.dim, :self.dim] = np.eye(self.dim) * (1 - rest_length/norm_x1x2) + np.outer(x1-x2, x1-x2) / norm_x1x2**3
        hessian[self.dim:, self.dim:] = np.eye(self.dim) * (1 - rest_length/norm_x1x2) + np.outer(x2-x1, x2-x1) / norm_x1x2**3
        hessian[:self.dim, self.dim:] = -np.eye(self.dim) * (1 - rest_length/norm_x1x2) - np.outer(x1-x2, x2-x1) / norm_x1x2**3
        hessian[self.dim:, :self.dim] = -np.eye(self.dim) * (1 - rest_length/norm_x1x2) - np.outer(x2-x1, x1-x2) / norm_x1x2**3

        return hessian
   ```


   Newton with FD:

   

https://github.com/user-attachments/assets/2ad6aca0-c361-44dc-baeb-e53f1bb44f98



   Newton with analitycal:

   

https://github.com/user-attachments/assets/b2c73900-f5b0-430e-b5ed-76b2e7db35a3

In both cases we get satysfying results, but the analitycal computation is faster.



## Task 4:
For the floor I defined the the added energy as 0 if ```y > floor_y``` where ```y``` is the y value of the point and ```floor_y``` is the y value of the floor (the plane y=fllor_y will be the "floor"), and otherwise: ```self.col_lamda * (self.floor_y - y)**2```, so we punish vertices that are far from the floor_y by their distance from it, squared.

For the ball, we punish the vertices in the ball by the squared differance between the radius and the distance between the point and the ball's center.


```py

class AddedFloorColliderEnergy(ElementEnergy):
    def __init__(self, dim=2):
        super().__init__(dim)
        global pinned_vertices, V

        self.col_lamda = 0 #1
        self.floor_y = -0.5 #-0.8 #0
    
    
    def energy(self, x1):
        y= x1[1]

        if y < self.floor_y:
            return self.col_lamda * (self.floor_y - y)**2
        return 0
    def gradient(self, x1):
        grad = np.zeros(self.dim)
        y = x1[1]

        if y < self.floor_y:
            grad[1] = 2 * self.col_lamda * (y-self.floor_y)
        
        return grad
    
    def hessian(self, x1):
        hessian = np.zeros((self.dim, self.dim))
        hessian[1, 1] = 2 * self.col_lamda
        return hessian
    
    
    def set_col_lamda(self, new_col_lamda):
        self.col_lamda = new_col_lamda



class AddedBallColiderEnergy(ElementEnergy):
    def __init__(self, dim=2):
        super().__init__(dim)
        global pinned_vertices, V

        self.ball_lamda = 0 #10

        # self.center = np.zeros(self.dim)
        self.center = np.ones(self.dim) * 0.5
        self.center[self.dim-1] = 0.3

        self.radius = 0.5
    
    def energy(self, x1):
        dist = np.linalg.norm(x1 - self.center)
        # print(f'AddedBallColiderEnergy: dist={dist}')
        if dist < self.radius:
            # print(f'AddedBallColiderEnergy: dist = {dist}, radius = {self.radius}')
            # print(f'AddedBallColiderEnergy: in if')
            return self.ball_lamda * (self.radius - dist)**2
        return 0
    def gradient(self, x1):

        grad = np.zeros(self.dim)
        dist = np.linalg.norm(x1 - self.center)

        if dist < self.radius:
            for i in range(self.dim):
                grad[i] = 2 * self.ball_lamda * (1 - self.radius/dist) * (x1[i] - self.center[i])
        
        return grad
    
    def hessian(self, x):
        hessian = np.zeros((self.dim, self.dim))
        dist = np.linalg.norm(x - self.center)

        if dist < self.radius:
            for i in range(self.dim):
                for j in range(self.dim):
                    if i == j:
                        hessian[i, i] = 2 * self.ball_lamda * ((x[i] - self.center[i])**2 / dist**3 + (1 - self.radius/dist))
                    else:
                        hessian[i, j] = 2 * self.ball_lamda * (x[i] - self.center[i]) * (x[j] - self.center[j]) / dist**3
                

        
        return hessian
    
    def set_ball_lamda(self, new_ball_lamda):
        self.ball_lamda = new_ball_lamda
 
```

To change the value for the floor's weight, the user presses the 'P'/';' keys.
In OnKeyboardPress:
```py
if event.keypress in ['p', 'P']:
        optimizer.set_col_lamda(optimizer.femMesh.added_floor_col_energy.col_lamda+1)
        print_to_window(f'current collider lamda : {optimizer.femMesh.added_floor_col_energy.col_lamda}')
        redraw()
    if event.keypress in ['semicolon', 'COLON']:
        print("; pressed")
        if optimizer.femMesh.added_floor_col_energy.col_lamda > 0:
            optimizer.set_col_lamda(optimizer.femMesh.added_floor_col_energy.col_lamda-1)
        
        print_to_window(f'current colider lamda : {optimizer.femMesh.added_floor_col_energy.col_lamda}')
        redraw()
```




https://github.com/user-attachments/assets/88cd9994-8838-4706-8afc-30642c1a7a43



https://github.com/user-attachments/assets/1cc78a52-1c5d-4df9-964a-cf457cf9afa9

