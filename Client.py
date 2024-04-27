from ChatClient import ChatClient
from VideoClient import VideoClient
import concurrent.futures
import threading
import asyncio
#Doesn't seem to be huge difference in speed when using 1 port or 2
#Problem closing video socket
#Doesn't seem to be large difference whem using video_client in normal thread type
#Error when disconnecting now in server side.Ingenreral disconnecting sucks and video is very slow
#Maybe use asynco instead
#Read more about Future objects
#Read about other version
class Client:
    def __init__(self,server_ip, server_port1,server_port2,client_ip,client_port,name):
    #Maybe client could have attribute name which will be passed to chatclient,videoclient
        self._chat_client = ChatClient(server_ip,server_port1,name)
        self._video_client = VideoClient(server_ip,server_port2,client_ip,client_port,name)
    """async def main(self):
        async for yielded_value in self._chat_client.main():
            # Process the yielded value
            print("Got yielded value:", yielded_value)

            # Check if the yielded value meets a specific condition
            if yielded_value == True:
                # Run another function asynchronously
                await self._video_client.main()

            # Get the returned value from the generator function
        returned_value = await self._chat_client.main()
        print("Returned value:", returned_value)"""
    def main(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self._chat_client.main)
            flag = future.result()
            print("flag=", flag)
            flag = next(future.result(), None)
            print("flag=", flag)

            if flag:
                #video_thread = threading.Thread(target=self._video_client.main)
                #   threads.append(receive_thread)
                #   threads.append(send_thread)
                #video_thread.start()
                executor.submit(self._video_client.main)

                flag = next(future.result(), None)
                print("flag=", flag)
                if flag == "exit":
                    #flag = next(future.result(), None)
                    #print("flag=", flag)
                    #self._video_client.__del__()
                    self._video_client.set_close_threads(True)
                    #executor.shutdown()


                # Wait for both threads to finish
                #video_thread.join()
"""        chat_thread = threading.Thread(target=self._chat_client.main)
        video_thread = threading.Thread(target=self._video_client.main)
        # threads.append(receive_thread)
        # threads.append(send_thread)
        chat_thread.start()
        video_thread.start()

        # Wait for both threads to finish
        chat_thread.join()
        video_thread.join()"""


"""generator = self._chat_client.main()
            valid = next(generator,None)

            if not valid:
                return
            else:
                valid = next(generator,None)
                if valid == "exit":
                    return
                #Once user decides to exit chat, all the other threads must end.Potential options: global variable which once the chatClient ends it executed closing all the other threads
                #Another option is like clientChat main function closing the threads in the same way.Write destructors for all the classes
                threads"""
