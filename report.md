# Reprot - Tom Shur 327615787
## Task 1:
1. Every time there is a callback to mouse right click, a red ball will be added on the surface of the objective function graph where the mouse cursor is:
   ![image](https://github.com/user-attachments/assets/ab3b3062-0862-4020-90ce-a2b41644b4b3)
    ![image](https://github.com/user-attachments/assets/5673c87f-66ae-44a7-af75-cd108a1b04c5)
![image](https://github.com/user-attachments/assets/afa76e1e-e7ec-4743-8e64-b27d80d9bdd7)
2. I initialized the graph in main:<br>
   ![image](https://github.com/user-attachments/assets/c6bb97a2-bc4e-4492-a9cf-202363a52d21) <br>
  and then updated it with a function called within OnMouseMove:
![image](https://github.com/user-attachments/assets/431612e4-26cb-4ea2-aedb-05862c844fd9)

https://github.com/user-attachments/assets/5676f4c3-52dd-4237-86e7-a6e470ab4ba4
3. I set an array of functions, as the current function is initialized to be the original function:
![image](https://github.com/user-attachments/assets/11a60d3f-abb9-4b6b-bf81-84bb7ecf8aff)
When the user presses the digit of a function, in the OnKeyPress callback: the previous arrows and balls are deleted, and with the function ChangeFunction, the current function changes to the appropriate function, the graph resets and the plot is rerendered.
![image](https://github.com/user-attachments/assets/caed1f6f-5fb1-496f-a5ab-0a1493ef2290)

https://github.com/user-attachments/assets/4b8a7560-b0da-4daa-90ac-f76932b85590

## Task 2:
1. I removed the part of the code that changes the path or renders arrows on the surface:
    ![image](https://github.com/user-attachments/assets/dfbe8dfa-df1a-430d-a673-a958142e0a1a)
2. Here is the function:
   ![image](https://github.com/user-attachments/assets/7c808644-3505-4b9b-98dd-5d065ebc8c9d)
   And the callback:
   
    ![image](https://github.com/user-attachments/assets/68202f95-8e5d-4beb-99a5-699b92613914)
3. I wrote a function do_step_GD that returns the next point in the gradient descent and renders the arrow, called with UpdateGraph() every time the key G on the keyboard is pressed.
   Also, to change the number of steps and to change the step size, the user can press the keys N or S appropriately, and enter the new value. I renamed Xi to Xi_GD.
   ![image](https://github.com/user-attachments/assets/13665e2a-2601-4218-afcd-748b52dc6564)
   ![image](https://github.com/user-attachments/assets/99a93e34-3744-4f59-8709-1e468bd75594)
   The values for num_steps and step_size are initialized in the main:
   ![image](https://github.com/user-attachments/assets/1c30de9f-2583-480f-b53a-ad746cd760ba)
   ![image](https://github.com/user-attachments/assets/2e33d35c-199d-4e55-a65a-37c9dc5b71de)
   after some trail and error, step_size = 0.2 is the best value I found.
   for step_size = 0.05:
   ![image](https://github.com/user-attachments/assets/6cd4a465-06ca-4cd4-aec7-836adf5deba1)
   0.1:
   ![image](https://github.com/user-attachments/assets/587a8a9b-7abf-4f13-96c0-b17f4d2029d4)
   0.2:
   ![image](https://github.com/user-attachments/assets/17e7ca74-f684-4ea7-8f0e-b2281f4488d4)
   0.3:
   ![image](https://github.com/user-attachments/assets/44b5bcfe-7be5-496d-8f0c-549a4bfac4a9)
   0.25:
   ![image](https://github.com/user-attachments/assets/2f7dc215-ce60-4eeb-8d59-bd8f8a823424)





## Task 3:
1 & 2 & 3. do_step() function is now more general and gets a the search direction function as a parameter:
![image](https://github.com/user-attachments/assets/1193a944-743b-4728-a371-07c7436a1d05)
Changed do_steps to each iteration do a GD and newton step and calculate the dot product between them:
![image](https://github.com/user-attachments/assets/b7c71aab-c213-4edd-8220-dac0737de7f6)
א
Added graphs for newton and the dot product:
![image](https://github.com/user-attachments/assets/21f655da-5b1d-4bee-968c-1bef453b457c)
![image](https://github.com/user-attachments/assets/3f6b41ab-42d1-48bb-9e32-32f066258646)

4. saddle point:
   ![image](https://github.com/user-attachments/assets/b87793bc-115a-4678-86f2-8be9fa88d3c6)
   maximum:
   ![image](https://github.com/user-attachments/assets/37e4250e-042c-45bd-895f-a3127a5b4083)
   Newton approachs the maximum / saddle point as the hassian is not PD there, while the GD goes to the closest minimum.

   minimum:
   ![image](https://github.com/user-attachments/assets/d061311d-b1ae-4440-9d6b-282910e235d0)
   Now both approach the minimum point, but the newton is a little faster and more stable than the GD.

## Task 4:
1.
   ![image](https://github.com/user-attachments/assets/8b3c5de4-cdce-4b7c-9dd3-8e36c257aa98)
2. I wrote 2 functions to change the hassian according to the 2 methods -
   1) Replace negative eigenvalues in (spectral decomposition) with a small value like 0.1 (after some trail and error, this value worked better for me than 0).
   2) Add some value bigger than the minimum eigenvalue to all eigenvalue.
   ![image](https://github.com/user-attachments/assets/eeb4389a-5c4b-4756-bd13-3b1ba92959aa)
   do_steps() function now takes a parameter neton_method and computes the hassian accordingly:
   ![image](https://github.com/user-attachments/assets/a6a707ab-2961-4c32-a7e9-3900b07876de)
3. I stop iterating once the gradient in the current point is very small (below some threshold, I took 0.01), as the grdient in a minimum is 0, or that the iteration number passed some threshold (after some expiriments, thw worst case numbers of iterations is about 45, so I took iter_threshold=75 just to be sure).
         ![image](https://github.com/user-attachments/assets/17b66ef7-c75a-4364-a13b-06b824741926)
         ![image](https://github.com/user-attachments/assets/6dcbdf3c-62b5-4f1b-898c-862cb4da6d4e)


   vanilla:
   ![image](https://github.com/user-attachments/assets/25a08808-1ba6-4191-9126-09f29e0efe53)
   ![image](https://github.com/user-attachments/assets/ec95fca6-09c8-4808-abcf-55577a496480)
   method 1:
   ![image](https://github.com/user-attachments/assets/231e733c-1203-4d93-b8d6-23c56a183981)

   ![image](https://github.com/user-attachments/assets/d01fb080-41d7-4ac4-9e94-9682d64d7a92)
   method 2:
   ![image](https://github.com/user-attachments/assets/8e3e9f2e-77c1-40ec-8440-1996b4ca7eb7)

   ![image](https://github.com/user-attachments/assets/3c13a15b-9665-44ff-bf81-b6336039d06e)

## Task 5:
1. 
```py analytical derivitives
      def gradient_analytical1(X):
          x, y = X[0], X[1]
          gx = y*np.cos(3*y)*np.cos(2*x*y)
          gy = x*np.cos(2*x*y)*np.cos(3*y) - 1.5*np.sin(3*y)*np.sin(2*x*y)
          return gx, gy
      
      def Hessian_analytical(X): # finite difference Hessian
          x, y = X[0], X[1]
          gxx = -2*(y**2)*np.cos(3*y)*np.sin(2*x*y)
          gyy = -x*(2*x*np.sin(2*x*y)*np.cos(3*y) + 3*np.sin(y)*np.cos(2*x*y)) - 1.5*(3*np.cos(3*y)*np.sin(2*x*y) + 2*x*np.cos(2*x*y)*np.sin(3*y))
          gxy = np.cos(3*y)*(np.cos(2*x*y)-2*x*y*np.sin(2*x*y)) - 3*y*np.sin(3*y)*np.cos(2*x*y)
          H = np.array([[gxx, gxy], [gxy, gyy]])
          return H
```
      
2.
   Ran each function on a list of 1000 points and checked the time:

```py analytical derivitives
points = np.random.rand(1000, 2) * 10  # 1000 points in 2D space

start_time = time.time()
for point in points:
    g = gradient_fd(objective_func1, point)
end_time = time.time()
t = end_time - start_time
t = round(t, 6)
print(f"FD Gradient: Time taken: {t} seconds")


start_time = time.time()
for point in points:
    g = gradient_analytical1(point)
end_time = time.time()
t = end_time - start_time
t = round(t, 6)
print(f"Analytical Gradient: Time taken: {t} seconds")

start_time = time.time()
for point in points:
    g = Hessian_fd(objective_func1, point)
end_time = time.time()
t = end_time - start_time
t = round(t, 6)
print(f"FD Hassian: Time taken: {t} seconds")

start_time = time.time()
for point in points:
    g = Hessian_analytical1(point)
end_time = time.time()
t = end_time - start_time
t = round(t, 6)
print(f"Analytical Hassian: Time taken: {t} seconds")


print("Done")
```
   

![image](https://github.com/user-attachments/assets/eebf5538-7967-4878-81f6-0b9a5bc0d8db)

3. 

```py analytical derivitives
points = np.random.rand(1000, 2) * 10  # 1000 points in 2D space


h_values = [0.1, 0.01, 0.001, 0.0001]

print("START")


for h in h_values:
    start_time = time.time()
    for point in points:
        g = gradient_fd(objective_func1, point, h)
    end_time = time.time()
    t = end_time - start_time
    t = round(t, 6)
    print(f"FD Gradient with h={h}: Time taken: {t} seconds")

print()
print()

start_time = time.time()
for point in points:
    g = gradient_analytical1(point)
end_time = time.time()
t = end_time - start_time
t = round(t, 6)
print(f"Analytical Gradient : Time taken: {t} seconds")

print()
print()

for h in h_values:
    start_time = time.time()
    for point in points:
        g = Hessian_fd(objective_func1 ,point, h)
    end_time = time.time()
    t = end_time - start_time
    t = round(t, 6)
    print(f"FD Hassian with h={h}: Time taken: {t} seconds")

print()
print()

start_time = time.time()
for point in points:
    g = Hessian_analytical1(point)
end_time = time.time()
t = end_time - start_time
t = round(t, 6)
print(f"Analytical Hassian with h={h}: Time taken: {t} seconds")


print("DONE")
```

   ![image](https://github.com/user-attachments/assets/b231a9d5-caa8-4050-8c8a-44dd08bc6a58)

