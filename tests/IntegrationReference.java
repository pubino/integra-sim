package integra;

import java.awt.Graphics;

/** Invokes the original integrator and samples its function without opening a window. */
public final class IntegrationReference extends IntegrationCanvas {
    @Override
    public void paint(Graphics graphics) {}

    public static void main(String[] args) {
        double[][] cases = {
            {-3, 3, 10, 1, 2, 0},
            {-2.4, 3.1, 17, -0.8, 1.7, 3},
            {2, 0.5, 50, 2.1, 3, -2},
            {-1.5, -1.5, 1, -0.3, -1.4, -1},
            {1, 2, 1000, 0.5, -2, 2},
            {-2, 2, 5, 0, 1, 0}
        };
        IntegrationReference model = new IntegrationReference();
        for (int sample = 0; sample < cases.length; sample++) {
            double[] v = cases[sample];
            model.integrate(v[0], v[1], (int) v[2], v[3], v[4], (int) v[5]);
            System.out.println("RULES," + sample + "," + model.rectrule() + "," + model.traprule());
            double dx = (model.highx - model.lowx) / model.n;
            for (int i = 0; i < model.n; i++) {
                double left = model.lowx + i * dx;
                double midpoint = left + dx / 2;
                System.out.println("INTERVAL," + sample + "," + i + "," + left + ","
                    + model.f(left) + "," + model.f(midpoint));
            }
            double curveStep = (model.highx - model.lowx) / 1000;
            for (int i = 0; i <= 1000; i++) {
                double x = model.lowx + i * curveStep;
                System.out.println("CURVE," + sample + "," + i + "," + x + "," + model.f(x));
            }
        }
    }
}
