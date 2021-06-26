#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <map>
#include <uns/uns.h>

using namespace std;

string input_directory = "../../input/";
string output_directory = "output/";

using DataDict = map<string, vector<float>>;

DataDict read_numerical_file(const string &filename, vector<string> fields) {
    DataDict output;

    for (string f : fields) {
        output[f] = vector<float>();
    }

    ifstream file(filename);
    
    while (file.peek() != EOF) { 
        for (string f : fields) {
            float curr;
            file >> curr;
            output[f].push_back(curr);
        }
    }

    file.close();

    return output;
}

int main() {
    vector<string> fields = {"x", "y", "z", "vx", "vy", "vz", "m"};
    DataDict data = read_numerical_file(input_directory + "host.txt", fields);

    cout << "Read data" << endl;    

    vector<float> pos;
    pos.insert(pos.end(), data["x"].begin(), data["x"].end());
    pos.insert(pos.end(), data["y"].begin(), data["y"].end());
    pos.insert(pos.end(), data["z"].begin(), data["z"].end());

    vector<float> vel;
    vel.insert(vel.end(), data["vx"].begin(), data["vx"].end());
    vel.insert(vel.end(), data["vy"].begin(), data["vy"].end());
    vel.insert(vel.end(), data["vz"].begin(), data["vz"].end());

    vector<float> mass;
    mass.insert(mass.end(), data["m"].begin(), data["m"].end());

    cout << "Created arrays" << endl;

    uns::CunsOut out = uns::CunsOut("output.tsf", "nemo", true);
    out.setData("pos", (int)pos.size(), &pos[0]);
    out.setData("vel", (int)vel.size(), &vel[0]);
    out.setData("mass", (int)mass.size(), &mass[0]);
    out.save();

    cout << "Data saved" << endl;

    return 0;
}