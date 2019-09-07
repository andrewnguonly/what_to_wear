# What to Wear?
Can't decide what to wear? Or maybe you forgot what you wore the other day and don't want to rewear the same thing? What to Wear? is a service for picking out what to wear everyday. Discover new outfits and wear your clothes more evenly!  

The service will send you an SMS message everyday (or configurable by day of the week).  
![What to Wear?](what_to_wear.jpg)

## Data Model
Data is modeled as documents. The document types described below are displayed as JSON. However, the JSON field types can be translated to an appropriate type for a given document store.

### users
Users of the service.
```json
{
    "created_at": 1567891563,
    "days": [true, true, true, true, true, false, false],
    "enabled": true,
    "first": "Andrew",
    "last": "Nguonly",
    "phone": "+18881234567"
}
```

### tops
Shirts, sweaters, or whatever you wear on the top.
```json
{

}
```

### bottoms
Pants, shorts, or whatever you wear on the bottom.
```json
{

}
```

### shoes
Sneakers, boots, or whatever you wear on the feet.
```json
{

}
```

### outfits
A selection of top, bottom, and shoe.
```json
{

}
```

## Deployment

### Environment Variables
`TWILIO_ACCOUNT_SID`: Twilio account SID.  
`TWILIO_AUTH_TOKEN`: Twilio auth token.  
`TWILIO_FROM_NUMBER`: Twilio number to send SMS from.  

### Google Cloud Firestore

### Google Cloud Functions

### Google Cloud Scheduler

### Twilio
Twilio is used to send SMS messages.