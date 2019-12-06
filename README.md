# Cinema 3 - (Extremely Simplified) Example of Microservices in Python


Overview
========

Cinema 3 is an example project which demonstrates the use of microservices for a fictional movie theater. 
The Cinema 3 backend was originally powered by 4 microservices, and currently has 5 services (7 in a neat future). all of which happen to be written in Python using Flask. For more information, you can refer to original blog post here: https://codeahoy.com/2016/07/10/writing-microservices-in-python-using-flask/

 * Movie Service: Provides information like movie ratings, title, etc.
 * Show Times Service: Provides show times information.
 * Booking Service: Provides booking information. 
 * Users Service: Provides movie suggestions for users by communicating with other services.
 * Rewards Service: Provides rewards for uses that have bought various tickets.

Requirements
===========

* Python 3 (Original package was based on python 2.7)
* Works on Linux, Windows, Mac OSX and (quite possibly) BSD.

Install
=======

The quick way is use the provided `make` file.

<code>
$ make install
</code>

Starting and Stopping Services
==============================

To launch the services:

<code>
$ make launch
</code>

To stop the services: 

<code>
$ make shutdown
</code>


APIs and Documentation
======================

## Movie Service (port 5001)

This service is used to get information about a movie. It provides the movie title, rating on a 1-10 scale, 
director and other information.

To lookup all movies in the database, hit: http://127.0.0.1:5001/movies

```

    GET /movies
    Returns a list of all movies.
    
    [
  {
    "director": "Richard Linklater",
    "id": 1,
    "rating": 10,
    "title": "Boyhood"
  },
  {
    "director": "Richard Linklater",
    "id": 2,
    "rating": 8,
    "title": "Before Sunset"
  },
  ...... output truncated ...... 
```

    

To lookup a movie by its id:
```
    GET /movies/3
    Returns the specified movie.
    
    {
      "director": "Richard Linklater",
      "id": 3,
      "rating": 9,
      "title": "Waking Life"
    }
``` 
## Showtimes Service (port 5002)

This service is used get a list of movies playing on a certain date.

To lookup all showtimes, hit: http://127.0.0.1:5002/showtimes

``` 
    GET /showtimes
    Returns a list of all showtimes by date.
    
   [
  {
    "date": "2019-11-01",
    "id": 1,
    "movie": 1
  },
  {
    "date": "2019-11-02",
    "id": 2,
    "movie": 2
  }, 
   ...... output truncated ...... 
```

To get movies playing on a certain date:
```
    GET /showtimes/2015-11-01
    Returns all movies playing on the date.
    [
      {
        "date": "2019-11-01",
        "id": 1,
        "movie": 1
      }
    ]
```

## Booking Service (port 5003)

Used to lookup booking information for users.

To get all bookings by all users in the system, hit: http://127.0.0.1:5003/bookings
```
    GET /bookings
    Returns a list of booking information for all bookings in the database.
   [
  {
    "date": "2019-11-01",
    "id": 1,
    "movie": 1,
    "rewarded": true,
    "user": 1
  },
  {
    "date": "2019-11-01",
    "id": 2,
    "movie": 2,
    "rewarded": true,
    "user": 2
  },
  ...... output truncated ...... 
```   
To lookup booking information for a user:
```
    GET /bookings/3
    [
      {
        "date": "2019-11-03",
        "id": 3,
        "movie": 3,
        "rewarded": true,
        "user": 3
      }
    ]
```

To make a new booking the POST request to http://127.0.0.1:5003/bookings/new must contain the following json:
        
    POST /bookings/new
    {
        "user" : 3,
        "date": "2020-01-01"
        "movie": 2
    }  

## User Service (port 5000)

This service returns information about the users of Cinema 3 and also provides movie suggestions to the 
users. It communicates with other services to retrieve booking or movie information.

To get a list of all the users in the system, hit: http://127.0.0.1:5000/users
```
    GET /users
    Returns a list of all users in the database.
    
    [
      {
        "id": 1,
        "name": "Jim Halpert"
      },
      {
        "id": 2,
        "name": "Dwight Schrute"
      },       
    ...... output truncated ...... 
```
To lookup information about a user you can use its id with this route: http://127.0.0.1:5000/1
```
    GET /users/1
    {
      "id": 1,
      "name": "Jim Halpert"
    }
```    

## Rewards Service (port 5004)

This service provides rewards for uses that have bought various tickets.
Everytime a user buy a new ticket his/her scores a new point on the reward service.

To get a list of all the users and their rewards score in the system, hit: http://127.0.0.1:5004/rewards
```
    GET /rewards
    [
      {
        "score": 0,
        "user": 1
      },
      {
        "score": 0,
        "user": 2
      },
    ..... output truncated .....
```
To lookup the score for a user, hit http://127.0.0.1:5004/rewards/2
```
    GET /rewards/2   
    {
        "score": 0,
        "user": 2
    }
```
To check if a user has enought point to get a reward, the GET request to http://127.0.0.1:5004/rewards/prizes/2.
The response will be like:
```
    GET /rewards/prizes/2
    {
        "points_until_prize": 0,
        "prize_avaliable": True,
        "user":2
    }
```
