package integra;

import java.awt.*;
import java.awt.event.*;
import java.awt.image.*;
import java.util.*;
import java.io.*;

import myutil.*;

public class Integra extends Panel implements ActionListener, SimApp
{
	TextField LOX;
	TextField HIX;
	TextField N;
	TextField A;
	TextField B;
	TextField K;

	Button IntButton;

	IntegrationCanvas ic;

        public static void main(String[] args) {
                new AppletFrame(new Integra(), 350, 500);
        }

	public void init()
	{
	    setLayout(new FlowLayout(FlowLayout.LEFT));
	    setBackground(Color.white);

	    LOX = new TextField("-3", 5);
	    HIX = new TextField(" 3", 5);
	    N   = new TextField("10", 5);
	    A   = new TextField("1", 5);
	    B   = new TextField("2", 5);
	    K   = new TextField("0", 5);

	    GridPanel gp = new GridPanel();

	    gp.add(new Label("Integration of: a x^k exp(-x^2/b)"),1,1,4,1);
	    gp.add(new Label("a:"), 1,2); gp.add(A, 2,2);
	    gp.add(new Label("b:"), 3,2); gp.add(B, 4,2);
	    gp.add(new Label("k:"), 5,2); gp.add(K, 6,2);
	    gp.add(new Label("Low x:" ), 1,3); gp.add(LOX, 2,3);
	    gp.add(new Label("High x:"), 3,3); gp.add(HIX, 4,3);
	    gp.add(new Label("n:"), 5,3); gp.add(N, 6,3);
	    gp.add(IntButton = new Button("Integrate"),1,4,2,1);
	    add(gp);

	    IntButton.addActionListener(this);

	    ic = new IntegrationCanvas();
	    add(ic);
	    ic.setSize(300,300);
	    validate();
	    setVisible(true);
	}

	public void start() {
		// No-op for this simulation
	}

        public void actionPerformed(ActionEvent e)
        {
	        if (e.getSource() == IntButton) {
			double lox = SL.atof(LOX.getText());
			double hix = SL.atof(HIX.getText());
			int    n = SL.atoi(N.getText());
			double a = SL.atof(A.getText());
			double b = SL.atof(B.getText());
			int    k = SL.atoi(K.getText());

			ic.integrate(lox, hix, n, a, b, k);
                }
        }
}

class IntegrationCanvas extends Canvas
{
	double lowx, highx, a, b;
	int n, k;

	public void integrate(double LOX, double HIX, int N,
			      double A, double B, int K)
	{
		lowx = LOX;
		highx = HIX;
		n = N;
		a = A;
		b = B;
		k = K;
		paint(getGraphics());
	}

	public void paint (Graphics g)
	{
		int i, j;

		double x, dx, fval, marginx, marginy;
		double lowy, highy;

	        GL.ginit(getGraphics(), getSize().width, getSize().height,
				this);

		dx = (highx - lowx)/n;

                /****************************************************
                * find lowy and highy
                ****************************************************/

                lowy = Double.MAX_VALUE;
                highy = -Double.MAX_VALUE;
                for (i=0; i<1000; i++) {
                        x = lowx + i*(highx-lowx)/1000;
                        if (f(x) < lowy) {
                                lowy = f(x);
                        }
                        if (f(x) > highy) {
                                highy = f(x);
                        }
                }

                /****************************************************
                * do the graphics
                ****************************************************/

                marginx = 0.1*(highx - lowx);
                marginy = 0.1*(highy - lowy);
                GL.ortho2( lowx-marginx, highx+marginx,
                        lowy-marginy, highy+marginy);

                GL.color(Color.black);     /* set current color to black */
                GL.clear();                /* fill window with black */

                /* draw x-axis */

                GL.color(Color.green);
                // linewidth(1);
                GL.move2(lowx,0.0);
                GL.draw2(highx,0.0);

                /* draw y-axis */

                GL.color(Color.green);
                // linewidth(1);
                GL.move2(0.0,lowy);
                GL.draw2(0.0,highy);

                /* first draw the rectangular rendition of f() */

                GL.color(Color.yellow);
		x = lowx;
                for (i=0; i<n; i++) {
                        fval = f(x+dx/2);
                        GL.pmv2(x,0);
                        GL.pdr2(x,fval);
                        GL.pdr2(x+dx,fval);
                        GL.pdr2(x+dx,0);
                        GL.pclos();
			x += dx;
                }

                /* then draw the trapezoidal rendition of f() */

                GL.color(Color.red);
		x = lowx;
                for (i=0; i<n; i++) {
                        GL.pmv2(x,0);
                        GL.pdr2(x,f(x));
                        GL.pdr2(x+dx,f(x+dx));
                        GL.pdr2(x+dx,0);
                        GL.pclos();
			x += dx;
                }

		GL.color(Color.white);
		GL.drawString("Rectangle   Rule: ", lowx, highy,
			"LEFT", "TOP");
		GL.drawString(Format.floating(12,6,rectrule()));

		GL.drawString("Trapezoidal Rule: ",
			lowx, 0.9*highy+0.1*lowy, "LEFT", "TOP");
		GL.drawString(Format.floating(12,6,traprule()));

                /* finally draw an accurate rendition of f() */

                n  = 1000;
                dx = (highx - lowx)/n;

                GL.color(Color.blue);
                // linewidth(1);
                fval = f(lowx);
                GL.move2(lowx,fval);
                for (i=0; i<=n; i++) {
                        x = lowx + i*dx;
                        fval = f(x);
                        GL.draw2(x,fval);
                }

		GL.swapbuffers();
	}

	double f( double x )
	{
	        return (a*Math.pow(x,k)*Math.exp(-x*x/b));
	}

	double rectrule()
	{
	        int i;
	        double area, x, dx;

	        dx = (highx - lowx)/n;

	        area = 0.0;
	        for (i=0; i<n; i++) {
	                x = lowx + i*dx + dx/2;
	                area += f(x);
	        }
	        area *= dx;

	        return (area);
	}

	double traprule()
	{
	        int i;
	        double area, x, dx;

	        dx = (highx - lowx)/n;

	        area = 0.0;
	        for (i=1; i<n; i++) {
	                x = lowx + i*dx;
	                area += f(x);
	        }
	        area += f(lowx)/2;
	        area += f(highx)/2;
	        area *= dx;

	        return (area);
	}
}
