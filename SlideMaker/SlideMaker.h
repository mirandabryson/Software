#ifndef ALEXBEAMER_H
#define ALEXBEAMER_H

#include "iostream"
#include "fstream"
#include <string.h>

class pres{
  public:
    pres(std::string keyColor_ = "black", bool center = false, bool madrid_ = false); 
    ~pres(); 
    void TitleSlide(std::string title);
    void OutputFile(std::string output); 
    void Underline(std::string uline); 
    void NewSlide(std::string options_string = "");
    void FinishSlide();
    void Title(std::string title); 
    void Text(std::string, std::string options_string = ""); 
    void FreeText(float x, float y, std::string text, std::string options_string = "");
    void StartBackup(); 

    //Templates
    void AllText(std::string options_string = ""); 
    void TextPlotPlot(std::string plot1, std::string plot2, std::string options = ""); 
    void TextPlot(std::string plot, std::string options_string = ""); 
    void Plot(std::string plot, std::string options_string = ""); 
    void Table(std::string table, std::string options_string = ""); 
    void TableText(std::string table, std::string options_string = ""); 
    void FourPlot(std::string plot1, std::string plot2, std::string plot3, std::string plot4, std::string options = ""); 
    void ThreeTable(std::string table1, std::string table2, std::string table3);
    void TextTableTable(std::string table1, std::string table2, std::string options = ""); 
    void TwoTable(std::string table1, std::string table2, std::string options = "");

  private:
    bool madrid;
    std::string keyColor;
    std::string output;
    std::string underline;
    ofstream myfile;
    int slideType; 
    int titleTwoLines; 
    float move_up;
    vector <float> top; 
    vector <float> bottom;
    vector <float> width;
    unsigned int nTextBoxes;
    void PlotType1(std::string options_string);
    void PlotType2(std::string plot1, std::string plot2, std::string options_string, float ar1, float ar2);
    void PlotType3(std::string plot1, std::string plot2, std::string options_string, float ar1, float ar2);
    void PlotType4(std::string plot, std::string options_string);
    void PlotType5(std::string plot, std::string options_string);
    void PlotType6(std::string table, std::string options_string);
    void PlotType7(std::string table, std::string options_string);
    void PlotType8(std::string plot1, std::string plot2, std::string plot3, std::string plot4, std::string options_string); 
    void PlotType9(std::string table1, std::string table2, std::string table3); 
    void PlotType10(std::string table1, std::string table2, std::string options_string);
};

#endif
