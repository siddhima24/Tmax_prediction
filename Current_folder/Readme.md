fetcher script returns the 5 weather parameters for a window of four days before the start date + today ( returns a data frame of features out of which we use the first four ( the required 4 days) for prediction ( the one Dhruv shared)


fetcher_script_Tmax returns a dataframe of temperature and month ( indexed by the dates) (just to compare the tmax values with the ones predicted)


model_training (trains and saves the model(district-wise) on historic data) (the one Riddhi shared)


prediction_script takes the 4-day parameters from the fetcher and uses the pre-trained model to predict the t max values for the next 15 days) (is currently performing very poorly)
<img width="300" height="363" alt="image" src="https://github.com/user-attachments/assets/15760a9a-6d43-483a-9e60-29a681153791" />   <img width="720" height="1600" alt="image" src="https://github.com/user-attachments/assets/405a20ff-d3f4-4a34-a588-f5e64f69b137" />


jan_rmse was just to check the prediction rmse scores for jan 2026, considering the temp.s from fetcher_script_tmax as the true Tmax values(very bad scores again)

<img width="408" height="428" alt="image" src="https://github.com/user-attachments/assets/bce430ff-203a-4946-a978-923026548082" />



