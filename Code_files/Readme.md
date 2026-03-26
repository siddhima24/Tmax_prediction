Download ERA5 district-level (month-by-month) data using the two download files via cds API. This data needs to be unzipped. (Latency = 5 days generally)

The temperature and Rainfall data can be directly downloaded from the IMD website. They are generally updated yearly.

These need to be converted into a csv file to train the model. The build_csv file performs this function. It changes the hourly ERA5 data into daily and performs IDW. It finally returns the 10-year master csv for a district.

The model training and prediction notebook trains and saves the models and scalars. It predicts the Tmax value for a set of 15 days from the date given as input using the data of the last 4 days from an API. (This version also computes the RMSE)
