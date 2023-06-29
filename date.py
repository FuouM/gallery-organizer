import datetime

timestamp = 1625023200123  # Replace this with your actual timestamp

# Convert milliseconds to seconds
seconds = timestamp / 1000

# Convert timestamp to a datetime object with precision
dt = datetime.datetime.utcfromtimestamp(seconds)

# Format the datetime object as a string
date = dt.strftime('%Y-%m-%d %H:%M:%S.%f')  # Change the format as per your requirement

print(date)