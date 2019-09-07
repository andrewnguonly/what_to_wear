# What to wear?
A service for picking out what to wear everyday.

## Data Model
Data are modeled as documents. The document types described below are displayed as JSON. However, the JSON field types can be translated to the appropriate type for a given document store.

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

### Environemnt Variables
`TWILIO_ACCOUNT_SID`: Twilio account SID.  
`TWILIO_AUTH_TOKEN`: Twilio auth token.  
`TWILIO_FROM_NUMBER`: Twilio number to send SMS from.  

### Google Cloud Functions

### Google Cloud Scheduler