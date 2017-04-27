import ROOT
import ppmUtils as utils

## do not use this manually! call plotDataMC with no h_data argument
def plotBackgrounds(h_bkg_vec_, bkg_names, canvas=None, stack=None, saveAs=None, xRangeUser=None, doPause=False, 
                    isLog=True, xAxisTitle="H_{T}", xAxisUnit="GeV", dataMax=0, userMax=None, userMin=None,
                    doLegend=False, doMT2Colors=False, doOverflow=True, shallowCopy=True):

    # make shallow copies of hists so we don't overwrite the originals
    if shallowCopy:
        h_bkg_vec = [ROOT.TH1D() for h in h_bkg_vec_]
        for i in range(len(h_bkg_vec_)):
            h_bkg_vec_[i].Copy(h_bkg_vec[i])
    else:
        h_bkg_vec = h_bkg_vec_

    if canvas==None:
        canvas = ROOT.TCanvas()
    if stack==None:
        stack = ROOT.THStack()

    if(isLog):
        canvas.SetLogy(1)

    canvas.cd()

    colors = [ROOT.kAzure+7, ROOT.kSpring-5, ROOT.kOrange-2, ROOT.kRed-7,
              ROOT.kCyan-7, ROOT.kMagenta-7, ROOT.kGray]

    nh = len(h_bkg_vec)
    
    for i in range(nh):
        if doMT2Colors:
            h_bkg_vec[i].SetFillColor(utils.GetMT2Color(bkg_names[i]))
        else:
            h_bkg_vec[i].SetFillColor(colors[nh-1-i])
        h_bkg_vec[i].SetLineColor(ROOT.kBlack)
        if doOverflow:
            utils.PutOverflowInLastBin(h_bkg_vec[i], None if xRangeUser==None else xRangeUser[1])

    for i in range(nh):
        stack.Add(h_bkg_vec[i])

    stack.Draw("HIST")

    if xRangeUser!=None:
        stack.GetXaxis().SetRangeUser(*xRangeUser)

    binWidth = utils.GetBinWidth(h_bkg_vec[0])
    if binWidth == None:  ## uneven binning
        binWidth = 'Bin'

    if xAxisUnit==None:
        stack.GetXaxis().SetTitle(xAxisTitle)
    else:
        stack.GetXaxis().SetTitle(xAxisTitle + " [{0}]".format(xAxisUnit))
    if binWidth != 'Bin':
        binWidth = str(round(binWidth,5)) + " " + (xAxisUnit if xAxisUnit!=None else "")
    stack.GetYaxis().SetTitle("Events / {0}".format(binWidth))
    stack.GetYaxis().SetTitleOffset(1.4)
    stack.GetXaxis().SetTitleOffset(1.2)

    utils.SetYBounds(stack, isLog, h_bkg_vec, dataMax, xRangeUser)
    if userMax!=None:
        stack.SetMaximum(userMax)
    if userMin!=None:
        stack.SetMinimum(userMin)

    ## legend
    if doLegend:
        leg = ROOT.TLegend(0.65,0.71,0.88,0.88)
        for i in range(len(h_bkg_vec)):
            leg.AddEntry(h_bkg_vec[-i-1],bkg_names[-i-1],"f")
        leg.Draw()

    if saveAs != None:
        canvas.saveAs(saveAs)
        
    if doPause:
        raw_input()

## make a ratio plot. For use within the plotDataMC and plotComparison functions
def plotRatio(h1, h2, canvas=None, ratioHist=None, xRangeUser=None, ratioTitle = None, markerSize=0.7, 
              doPull=False, convertToPoisson=False, ratioGraph=None, drawZeros=True, drawSystematicBand=False,
              systematics=None, h_syst=None, yRangeUser=None):

    if doPull:
        convertToPoisson = False

    if canvas==None:
        canvas = ROOT.TCanvas()
    if ratioHist==None:
        ratioHist = ROOT.TH1D()

    if convertToPoisson and type(ratioGraph)!=type(ROOT.TGraphAsymmErrors()):
        raise RuntimeError("must pass a TGraphAsymmErrors as ratioGraph for convertToPoisson option!")

    if ratioTitle==None:
        if not doPull:
            ratioTitle = "Data/MC"
        else:
            ratioTitle = "Pull"

    canvas.cd()
    canvas.SetTicky(1)

    if not doPull:
        h2.Copy(ratioHist)
        ratioHist.Divide(h1)
        if convertToPoisson:
            utils.GetPoissonRatioGraph(h1,h2,ratioGraph,drawZeros=drawZeros)
    else:
        nbins = h1.GetNbinsX()
        h2.Copy(ratioHist)
        for i in range(1,nbins+1):
            diff = h2.GetBinContent(i)-h1.GetBinContent(i)
            err = ROOT.TMath.Sqrt(h2.GetBinError(i)**2 + h1.GetBinError(i)**2)
            ratioHist.SetBinContent(i,diff/err)
            ratioHist.SetBinError(i,1.0)

    ratioHist.SetTitle("")
    #yaxis
    if not doPull:
        if yRangeUser == None:
            ratioHist.GetYaxis().SetRangeUser(0,2)
        else:
            ratioHist.GetYaxis().SetRangeUser(yRangeUser[0],yRangeUser[1])            
        ratioHist.GetYaxis().SetNdivisions(505)
    else:
        if yRangeUser == None:
            ratioHist.GetYaxis().SetRangeUser(-4,4)
        else:
            ratioHist.GetYaxis().SetRangeUser(yRangeUser[0],yRangeUser[1])            
        ratioHist.GetYaxis().SetNdivisions(204,False)
    ratioHist.GetYaxis().SetTitle(ratioTitle)        
    ratioHist.GetYaxis().SetTitleSize(0.18)
    ratioHist.GetYaxis().SetTitleOffset(0.17)
    ratioHist.GetYaxis().SetLabelSize(0.13)
    ratioHist.GetYaxis().CenterTitle()
    #xaxis
    ratioHist.GetXaxis().SetLabelSize(0.0)
    ratioHist.GetXaxis().SetTitle("")
    ratioHist.GetXaxis().SetTickSize(0.06)
    #markers
    ratioHist.SetMarkerStyle(20)
    ratioHist.SetMarkerSize(markerSize)    
    if convertToPoisson:
        ratioGraph.SetMarkerStyle(20)
        ratioGraph.SetMarkerSize(markerSize)
        ratioHist.Reset()
        ratioHist.Draw()
        ratioGraph.Draw("PZ")
    else:
        ratioHist.Draw("PE")

    # systematics
    if drawSystematicBand:
        h1.Copy(h_syst)
        for i in range(1,h_syst.GetNbinsX()+1):
            h_syst.SetBinContent(i,1)
            h_syst.SetBinError(i, systematics[i-1])
        h_syst.SetFillStyle(1001)
        h_syst.SetFillColor(ROOT.kGray+0)
        h_syst.Draw("SAME E2")

    #line
    line = ROOT.TLine()
    line.SetLineColor(ROOT.kGray+2)
    line.SetLineWidth(2)
    line.SetLineStyle(7)
    xmin = ratioHist.GetXaxis().GetBinLowEdge(1)
    xmax = ratioHist.GetXaxis().GetBinUpEdge(h1.GetNbinsX())
    if xRangeUser!=None:
        xmin = xRangeUser[0]
        xmax = xRangeUser[1]
    if not doPull:
        line.DrawLine(xmin,1,xmax,1)
    else:
        line.DrawLine(xmin,0,xmax,0)
        line.SetLineColor(ROOT.kGray)
        line.SetLineWidth(1)
        line.SetLineStyle(1)
        line.DrawLine(xmin,1,xmax,1)
        line.DrawLine(xmin,2,xmax,2)
        line.DrawLine(xmin,3,xmax,3)
        line.DrawLine(xmin,-1,xmax,-1)
        line.DrawLine(xmin,-2,xmax,-2)
        line.DrawLine(xmin,-3,xmax,-3)
    if convertToPoisson:
        ratioGraph.Draw("SAME PZ")
    else:
        ratioHist.Draw("SAME PE")
    ratioHist.Draw("SAMEAXIS")


## plot data and stacked background hist. See README for argument explanations
def plotDataMC(h_bkg_vec_, bkg_names, h_data=None, title=None, subtitles=None, doRatio=True, scaleMCtoData=False, saveAs=None, 
               isLog=True, dataTitle="Data", xRangeUser=None, doPause=False, lumi=1.0, lumiUnit="fb", noLumi=False,
               energy=13, xAxisTitle="H_{T}", xAxisUnit="GeV", userMax=None, userMin=None, doSort=False,
               doMT2Colors=False, markerSize=0.9, doOverflow=True, titleSize=0.04, subtitleSize=0.03, subLegText=None,
               subLegTextSize=0.03, cmsText="CMS Preliminary", cmsTextSize=0.035, doBkgError=False, functions=[], 
               legCoords=None, doPull=False, convertToPoisson=False, drawZeros=True, drawSystematicBand=False, systematics=None,
               h_sig_vec=[], sig_names=[]):
    
    if h_data == None:
        doRatio = False
        scaleMCtoData = False
        
    if drawSystematicBand and systematics==None:
        raise RuntimeError("Must supply a list of systematics to draw uncertainty band!")

    if systematics != None and len(systematics) != h_bkg_vec_[0].GetNbinsX():
        raise RuntimeError("length of systematics list does not equal the number of bins!")
        
    # make shallow copies of hists so we don't overwrite the originals
    h_bkg_vec = [ROOT.TH1D() for h in h_bkg_vec_]
    for i in range(len(h_bkg_vec_)):
        h_bkg_vec_[i].Copy(h_bkg_vec[i])
    if h_data != None:
        if type(h_data) != type(list()):
            h_data = [h_data]
        if len(h_data) > 4:
            raise RuntimeError("currently only supports up to 4 data histograms!")
        h_data_ = [ROOT.TH1D() for h in h_data]
        for i in range(len(h_data)):
            h_data[i].Copy(h_data_[i])
            h_data[i] = h_data_[i]  #so the arg name doesn't have underscore

    ROOT.gStyle.SetOptStat(0)
     
    #### setup canvas and pads ####

    c = ROOT.TCanvas()
    
    if doRatio:
        c.SetCanvasSize(700,600)
        pads = []
        pads.append(ROOT.TPad("1","1",0.0,0.16,1.0,1.0))
        pads.append(ROOT.TPad("2","2",0.0,0.0,1.0,0.17))
        
        pads[0].SetTopMargin(0.08)
        pads[0].SetLeftMargin(0.12)
        pads[0].SetBottomMargin(0.10)
        pads[1].SetLeftMargin(0.12)
        
        pads[0].Draw()
        pads[1].Draw()
        pads[0].cd()
    else:
        c.SetCanvasSize(700,504)
        pads = [c]
        pads[0].SetLeftMargin(0.12)
        pads[0].SetTopMargin(0.08)

    if isLog:
        pads[0].SetLogy()
    pads[0].SetTicky(1)

    pads[0].cd()

    ## MC
    int_errors = [ROOT.Double(0) for i in range(len(h_bkg_vec))]
    integrals = [h_bkg_vec[i].IntegralAndError(0,-1,int_errors[i]) for i in range(len(h_bkg_vec))]
    if doSort:
        zipped = zip(h_bkg_vec,bkg_names)
        sorted_bkg = [x for (y,x) in sorted(zip(integrals,zipped))]
        h_bkg_vec = [x for (x,y) in sorted_bkg]
        bkg_names = [y for (x,y) in sorted_bkg]
    else:
        h_bkg_vec = h_bkg_vec[::-1]
        bkg_names = bkg_names[::-1]

    scaleFactor = 1.0
    scaleFactorError = 1.0
    if(h_data!=None and scaleMCtoData):
        tot_MC_error = ROOT.TMath.Sqrt(sum([x**2 for x in int_errors]))
        tot_MC_integral = sum(integrals)
        data_error = ROOT.Double(0)
        data_integral = h_data[0].IntegralAndError(0,-1,data_error)
        scaleFactor = data_integral/tot_MC_integral
        scaleFactorError = scaleFactor * (data_error/data_integral + tot_MC_error/tot_MC_integral)
    for i in range(len(h_bkg_vec)):
        h_bkg_vec[i].Scale(scaleFactor)

    dataMax = 0
    if h_data!=None:
        for ih in range(len(h_data)):
            for i in range(1,h_data[ih].GetNbinsX()+1):
                y = h_data[ih].GetBinContent(i)+h_data[ih].GetBinError(i)
                if y>dataMax:
                    dataMax = y

    stack = ROOT.THStack("hs","")
    plotBackgrounds(h_bkg_vec, bkg_names, canvas=pads[0], stack=stack, xRangeUser=xRangeUser, isLog=isLog, 
                    xAxisTitle=xAxisTitle, xAxisUnit=xAxisUnit, dataMax=dataMax, shallowCopy=False,
                    userMax=userMax, userMin=userMin, doMT2Colors=doMT2Colors, doOverflow=doOverflow)

    if doBkgError:
        h_err = ROOT.TH1D()
        h_bkg_vec[0].Copy(h_err)
        for i in range(1,len(h_bkg_vec)):
            h_err.Add(h_bkg_vec[i])
        h_err.SetFillStyle(3244)
        h_err.SetFillColor(ROOT.kGray+3)
        h_err.Draw("E2SAME")


    ## data
    if h_data != None:
        styles = [20,24,21,25]
        N_DATA_EVENTS = int(h_data[0].GetEntries()) #curretly only support counting of events for first histogram
        for ih in range(len(h_data)):
            h_data[ih].SetMarkerStyle(styles[ih])
            h_data[ih].SetMarkerSize(markerSize)
            h_data[ih].SetMarkerColor(ROOT.kBlack)
            h_data[ih].SetLineColor(ROOT.kBlack)
            if xRangeUser!=None:
                h_data[ih].GetXaxis().SetRangeUser(*xRangeUser)
            if doOverflow:
                utils.PutOverflowInLastBin(h_data[ih], None if xRangeUser==None else xRangeUser[1])
        if convertToPoisson:
            h_data_poisson = [ROOT.TGraphAsymmErrors() for h in h_data]
            for ih in range(len(h_data)):
                utils.ConvertToPoissonGraph(h_data[ih], h_data_poisson[ih], drawZeros=drawZeros)
                h_data_poisson[ih].SetMarkerStyle(styles[ih])
                h_data_poisson[ih].SetMarkerSize(markerSize)
                h_data_poisson[ih].SetMarkerColor(ROOT.kBlack)
                h_data_poisson[ih].SetLineColor(ROOT.kBlack)
                h_data_poisson[ih].Draw("SAME PZ")
        else:
            for ih in range(len(h_data)):
                h_data[ih].Draw("SAME E0")

    ## functions
    for function in functions:
        function.Draw("SAME")

    ## signals
    sig_cols = [ROOT.kMagenta, ROOT.kCyan, ROOT.kOrange+7, ROOT.kGreen]
    for isig in range(len(h_sig_vec)):
        h_sig_vec[isig].SetLineColor(sig_cols[isig])
        h_sig_vec[isig].SetLineWidth(2)
        h_sig_vec[isig].Draw("SAME HIST")

    ## legend
        
    if legCoords == None:
        legCoords = (0.65,0.72,0.87,0.89)
    leg = ROOT.TLegend(*legCoords)
    if h_data != None:
        if type(dataTitle) != type(list()):
            dataTitle = [dataTitle]
        for ih in range(len(h_data)):
            leg.AddEntry(h_data[ih],dataTitle[ih])
    for i in range(len(h_bkg_vec)):
        leg.AddEntry(h_bkg_vec[-i-1],bkg_names[-i-1],"f")
    for i in range(len(h_sig_vec)):
        leg.AddEntry(h_sig_vec[i], sig_names[i], "l")
    leg.Draw()
    
    # handle all of the text
    text = ROOT.TLatex()
    text.SetNDC(1)
    cursorX = 0.23
    cursorY = 0.89
    # title
    if title!=None and title!="":
        text.SetTextAlign(13) 
        text.SetTextFont(42)
        text.SetTextSize(titleSize)
        text.DrawLatex(cursorX,cursorY,title)
        cursorY -= titleSize + 0.010
    # subtitles
    if subtitles==None:
        subtitles=[]
    if type(subtitles)==type(""):
        subtitles = [subtitles]
    for s in subtitles:
        text.SetTextAlign(13)
        text.SetTextFont(42)
        text.SetTextSize(subtitleSize)
        text.DrawLatex(cursorX,cursorY,s)
        cursorY -= subtitleSize + 0.015
    # lumi
    if not noLumi:
        utils.DrawLumiText(pads[0],lumi=lumi,lumiUnit=lumiUnit,energy=energy,textFont=42,textSize=cmsTextSize)
    # CMS text
    utils.DrawCmsText(pads[0],text=cmsText,textFont=62,textSize=cmsTextSize)
    # Sub-legend text
    cursorX = legCoords[0]
    cursorY = legCoords[1]-0.01
    if subLegText==None:
        subLegText=[]
    if type(subLegText)==type(""):
        subLegText = [subLegText]
    for s in subLegText:
        if h_data==None:
            N_DATA_EVENTS = 1
        vals = (N_DATA_EVENTS,scaleFactor,scaleFactorError)
        s = s.replace("{ndata}","{0:d}")
        s = s.replace("{datamcsf}","{1:.2f}")
        s = s.replace("{datamcsferr}","{2:.2f}")
        text.SetTextFont(62)
        text.SetTextAlign(13)
        text.SetTextSize(subLegTextSize)
        text.DrawLatex(cursorX,cursorY,s.format(*vals))
        cursorY -= 0.03+0.005


    ######## ratio plot ############
    
    if doRatio:
        pads[1].cd()
    
        h1 = ROOT.TH1D()
        h_bkg_vec[0].Copy(h1)
        for i in range(len(h_bkg_vec)-1):
            h1.Add(h_bkg_vec[i+1])
        ratioHist = ROOT.TH1D()
        ratioGraph = ROOT.TGraphAsymmErrors()
        h_syst = ROOT.TH1D()

        # currently only support drawing ratio for one data histogram. Uses the first one in the list.
        plotRatio(h1, h_data[0], canvas=pads[1], ratioHist=ratioHist, xRangeUser=xRangeUser, markerSize=markerSize,
                  doPull=doPull, convertToPoisson=convertToPoisson, ratioGraph=ratioGraph, drawZeros=drawZeros,
                  drawSystematicBand=drawSystematicBand, systematics=systematics, h_syst=h_syst)
    
    c.Update()
    c.SetWindowSize(c.GetWw()+4, c.GetWh()+50)

    if saveAs!=None:
        c.SaveAs(saveAs)

    if doPause:
        raw_input()

## make a comparison plot between two histograms. Plots both histos on one axis, as well as a ratio plot
def plotComparison(h1_, h2_, title="", ratioTitle="Data/MC", h1Title="MC", h2Title="Data", saveAs=None,
                   size=(700,600), xRangeUser=None, markerSize=0.65, doPause=False, isLog=True,
                   normalize=False, xAxisTitle="", ratioYRange=None):

    h1 = ROOT.TH1D()
    h1_.Copy(h1)
    h2 = ROOT.TH1D()
    h2_.Copy(h2)

    if normalize:
        if h1.Integral(0,-1) > 0:
            h1.Scale(1.0/h1.Integral(0,-1)/h1.GetBinWidth(1))
        if h2.Integral(0,-1) > 0:
            h2.Scale(1.0/h2.Integral(0,-1)/h2.GetBinWidth(1))

    ROOT.gStyle.SetOptStat(0)

    c = ROOT.TCanvas()
    c.SetCanvasSize(size[0],size[1])

    pads = []
    pads.append(ROOT.TPad("1","1",0.0,0.16,1.0,1.0))
    pads.append(ROOT.TPad("2","2",0.0,0.0,1.0,0.17))

    pads[0].SetLogy(isLog)
    pads[0].SetTopMargin(0.09)
    pads[0].SetLeftMargin(0.12)
    pads[0].SetBottomMargin(0.10)
    pads[1].SetLeftMargin(0.12)
    
    pads[0].Draw()
    pads[1].Draw()
    pads[0].cd()
        
    h1.SetTitle(title)
    h1.SetLineColor(ROOT.kRed)
    h1.GetXaxis().SetTitleOffset(1.15)
    if xRangeUser!=None:
        h1.GetXaxis().SetRangeUser(*xRangeUser)
        h2.GetXaxis().SetRangeUser(*xRangeUser)
    if normalize:
        h1.GetYaxis().SetTitle("Normalized")
    else:
        h1.GetYaxis().SetTitle("Entries / {0} GeV".format(h1.GetXaxis().GetBinWidth(1)))
    h1.GetYaxis().SetTitleOffset(1.2)
    h1.GetXaxis().SetTitle(xAxisTitle)
    h2.SetLineColor(ROOT.kBlack)
    h2.Draw("PE")
    h1.Draw("SAME PE")
    
    leg = ROOT.TLegend(0.60,0.75,0.89,0.89)
    leg.AddEntry(h1, h1Title)
    leg.AddEntry(h2, h2Title)
    leg.Draw()
    
    ######## ratio plot ############
    
    pads[1].cd()
    ratio = ROOT.TH1D()
    plotRatio(h1,h2,canvas=pads[1], ratioHist=ratio, ratioTitle=ratioTitle, xRangeUser=xRangeUser, 
              markerSize=markerSize, yRangeUser=ratioYRange)

    c.Update()
    c.SetWindowSize(c.GetWw()+4, c.GetWh()+50)

    if saveAs!=None:
        c.SaveAs(saveAs)

    if doPause:
        raw_input()








