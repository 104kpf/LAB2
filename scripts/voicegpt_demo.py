#!/usr/bin/env python3
import speech_recognition as sr
import rospy
from std_msgs.msg import String
import httpx
import threading
# obtain audio from the microphone
r = sr.Recognizer()


# =======================
# OpenAI (Azure) Configuration
# =======================
# Replace these values with your own settings.
api_key = "Your API Key"  # Your API key
api_base = "https://models.inference.ai.azure.com"  
deployment_id = "gpt-4o"  
api_version = "2023-03-15-preview"  


http_client = httpx.Client(
    base_url=api_base,
    follow_redirects=True,
)

def get_chat_completion(messages, model=deployment_id):
    """
    Sends a chat completion request to the Azure OpenAI endpoint using httpx.
    """
    url = f"/openai/deployments/{deployment_id}/chat/completions?api-version={api_version}"
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
    }
    payload = {
        "model": model,
        "messages": messages,
    }
    response = http_client.post(url, headers=headers, json=payload)
    response.raise_for_status()  # Raises an HTTPError for bad responses
    return response.json()

def user_message_callback(user_text):
    """
    Sends the recognized text to GPT and publishes the GPT response via ROS.
    """
    rospy.loginfo("Received user input: %s", user_text)
    messages = [
        {
        "role": "system",
        "content": (
            "You are a helpful ROS assistant specifically for controlling a TurtleBot. You will be asked for generate specific path for turtle to following.(example:rectangle path with side length 2m.) "
            "Please provide responses in the following JSON format for a combination of moving forward "
            "and then rotating in place:\n\n"
            "{\n"
            "  \"action\": \"move\",\n"
            "  \"speed\": {\n"
            "    \"linear\": {\n"
            "      \"x\": [linear speed value for moving forward or backward],\n"
            "      \"y\": 0\n"
            "    },\n"
            "    \"angular\": {\n"
            "      \"x\": 0,\n"
            "      \"y\": 0\n"
            "    }\n"
            "  },\n"
            "  \"distance\": [distance value],\n"
            "  \"angular_speed\": {\n"
            "    \"linear\": {\n"
            "      \"x\": [value]\n"
            "    },\n"
            "    \"angular\": {\n"
            "      \"z\": [angular speed value for rotation]\n"
            "    }\n"
            "  }\n"
            "}\n\n"
            "The 'speed' value controls the linear speed for moving forward or backward (use positive values "
            "for forward movement and negative values for backward movement). The 'distance' specifies how far "
            "to move before rotating. The 'angular_speed' controls the angular velocity for rotating in place "
            "after moving (use positive values for left turns and negative values for right turns).\n\n"
            "Please provide only a plain JSON object without any markdown formatting"
        )
    },
        {"role": "user", "content": user_text}
    ]
    try:
        chat_completion = get_chat_completion(messages)
        # Extract GPT's reply from the response
        gpt_reply = chat_completion["choices"][0]["message"]["content"]
        rospy.loginfo("GPT reply: %s", gpt_reply)
        gpt_reply_pub.publish(gpt_reply)
    except Exception as e:
        rospy.logerr("Error during chat completion: %s", e)

def speech_recognition_loop():
    """
    Continuously performs speech recognition in a separate thread and sends the recognized text to GPT.
    """
    recognizer = sr.Recognizer()
    while not rospy.is_shutdown():
        try:
            with sr.Microphone() as source:
                rospy.loginfo("Please speak...")
                audio = recognizer.listen(source)
            try:
                # Use Sphinx for offline speech recognition (alternatively, you can use Google Speech API, etc.)
                recognized_text  = r.recognize_google(audio, language="zh-CN")
                rospy.loginfo("Recognized text: %s", recognized_text)
                user_message_callback(recognized_text)
            except sr.UnknownValueError:
                rospy.logwarn("Could not understand the audio")
            except sr.RequestError as e:
                rospy.logerr("Speech recognition error: %s", e)
        except Exception as e:
            rospy.logerr("Error during recording: %s", e)

def main():
    rospy.init_node('chatgpt_ros_node', anonymous=True)
    global gpt_reply_pub
    # Initialize ROS publisher for sending GPT replies
    gpt_reply_pub = rospy.Publisher("gpt_reply_to_user", String, queue_size=10)
    # Optionally, subscribe to other ROS topics if needed
    # rospy.Subscriber("user_to_gpt", String, user_message_callback)

    # Start the speech recognition thread
    sr_thread = threading.Thread(target=speech_recognition_loop)
    sr_thread.daemon = True
    sr_thread.start()

    # Keep the ROS node running
    rospy.spin()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass