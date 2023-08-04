import csv
import os


class profiler:

    def __init__(self, motor_profile: str):
        # Open the motor profile directory
        self.motor_profile = motor_profile
        self.motor_profile_dir = os.path.join(os.getcwd(), self.motor_profile)

        # Load each rpm file and calculate the feedforward gain
        # The naming convention is {rpm}rpm.csv
        self.ff_gains = {}
        for file in os.listdir(self.motor_profile_dir):
            if file.endswith(".csv"):
                rpm = int(file.split("rpm")[0])
                self.ff_gains[rpm] = self.calculate_ff(file)

        # Sort the rpm values
        self.ff_gains = dict(sorted(self.ff_gains.items()))

        print(self.create_c_struct())

    def calculate_ff(self, file: str):
        # Calculate the feedforward gain for a given rpm
        torque_samples = []
        # Open the file
        with open(os.path.join(self.motor_profile_dir, file), "r") as f:
            reader = csv.reader(f, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
            # Skip the header
            next(reader)
            # Read the data
            for row in reader:
                torque_samples.append(float(row[2]))

        # Calculate the average torque
        avg_torque = sum(torque_samples) / len(torque_samples)
        return avg_torque

    def create_c_struct(self):
        # Create a feed forward gain c struct formatted as follows:
        """
        struct feedforward_struct{
            bool     symmetric;  // Whether or not the feedforward can be assumed to be mirrored
            uint16_t size;
            float_t* setpoints;  // Unit RPS
            float_t* ff_gains;   // Unit NM
        };
        """
        # Create the setpoints and ff_gains strings
        setpoints = "{"
        ff_gains = "{"
        for rpm, ff_gain in self.ff_gains.items():
            setpoints += f"{rpm}, "
            ff_gains += f"{ff_gain}, "

        # Remove the trailing comma and space
        setpoints = setpoints[:-2] + "}"
        ff_gains = ff_gains[:-2] + "}"

        return f"""feedforward_struct ff = {'{'}
    true,
    {len(self.ff_gains)},
    new float_t[{len(self.ff_gains)}]{setpoints},
    new float_t[{len(self.ff_gains)}]{ff_gains}
{'}'};"""


if __name__ == "__main__":
    profiler = profiler("motor_profile_2023-06-23_09-48-25")

